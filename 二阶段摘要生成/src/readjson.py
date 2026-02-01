import json
import os
import time
import torch
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from tqdm import tqdm

# ================= 激进配置区域 =================
API_KEY = "sk-368e11c3ac0048f485f16ad3bfff06de"
BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-chat"

INPUT_FILE = r"C:\Users\ZJH\PycharmProjects\pythonProject\二阶段摘要生成\dist\experiment_evidence_subset.json"
OUTPUT_FILE = "final_experiment_results_aggressive.json"

# 🔥 激进并发：设置为 5 到 10
MAX_WORKERS = 5

# ===============================================

file_lock = threading.Lock()

print("正在初始化本地模型...")
# 自动开启 HuggingFace 国内镜像加速
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

try:
    embedder = SentenceTransformer('all-MiniLM-L6-v2', device='cuda' if torch.cuda.is_available() else 'cpu')
    nli_model = pipeline("text-classification", model='roberta-large-mnli',
                         device=0 if torch.cuda.is_available() else -1)
    print("✅ 本地模型加载完成")
except:
    print("❌ 本地模型加载失败，将跳过评估")
    embedder = None
    nli_model = None

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


def call_llm(prompt, system_prompt="You are a helpful assistant."):
    """
    针对 DeepSeek '排队机制' 优化的调用函数
    """
    max_retries = 3

    for attempt in range(max_retries):
        try:
            # print(f"  ...正在发送请求 (尝试 {attempt+1})") # 调试用
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                stream=False,
                # ⚠️⚠️⚠️ 这里的温度改回 0.3，1.3 太高了会导致乱码
                temperature=0.3,
                max_tokens=1024,

                # 🔥 关键修改：超时设置为 600 秒 (10分钟)
                timeout=600
            )
            return response.choices[0].message.content

        except Exception as e:
            error_msg = str(e)
            print(f"\n⚠️ 请求遇到问题: {error_msg[:100]}... (重试中)")
            time.sleep(2)

    return None


def generate_draft(evidence_list, topic_keywords, feedback=None):
    # 保持原有逻辑
    evidence_text = "\n".join([f"[ID:{i}] {sent}" for i, sent in enumerate(evidence_list)])
    topics_text = ", ".join(topic_keywords)
    prompt = f"""
    You are an academic summarization expert.

    ### INPUT DATA
    TOPIC KEYWORDS: {topics_text}
    EXTRACTED EVIDENCE:
    {evidence_text}

    ### REQUIREMENTS
    1. **Faithfulness**: Based strictly on Evidence.
    2. **Citation**: Include citation IDs, e.g., "Text [0, 2]."
    3. **Format**: JSON list of objects with "text" and "citations".

    ### FEEDBACK
    {feedback if feedback else "None"}

    Output ONLY JSON:
    """
    content = call_llm(prompt, system_prompt="You are a JSON generator.")
    if content:
        content = content.replace("```json", "").replace("```", "").strip()
    return content


def evaluate_summary(generated_json_str, evidence_list, topic_keywords):
    try:
        data = json.loads(generated_json_str)
    except:
        return False, "Format Error"

    feedback_msgs = []

    # 1. 幻觉检测
    if nli_model:
        for i, item in enumerate(data):
            summ_sent = item.get('text', "")
            raw_ids = item.get('citations', [])

            # =========== 🔥 修复核心：清洗引用ID ===========
            valid_ids = []
            for rid in raw_ids:
                try:
                    rid_int = int(rid)
                    if 0 <= rid_int < len(evidence_list):
                        valid_ids.append(rid_int)
                except:
                    pass
            # ===============================================

            premise = " ".join([evidence_list[rid] for rid in valid_ids])

            if not premise: continue

            # 截断防止爆显存
            premise = premise[:512]

            try:
                res = nli_model(f"{premise} </s> {summ_sent}")[0]
                if res['label'] == 'CONTRADICTION':
                    feedback_msgs.append(f"Sentence {i + 1} contradicts evidence.")
            except Exception as e:
                # 忽略极少数的 Tokenizer 长度报错
                pass

    # 2. 覆盖度检测
    if embedder:
        full_summary = " ".join([d.get('text', '') for d in data])
        missing = [t for t in topic_keywords if t.lower() not in full_summary.lower()]
        if len(missing) > len(topic_keywords) * 0.5:
            feedback_msgs.append(f"Missing topics: {', '.join(missing[:3])}.")

    if not feedback_msgs:
        return True, "PASS"
    else:
        return False, " ".join(feedback_msgs)


def process_single_sample(item):
    sample_id = item['id']
    evidence = item.get('extracted_evidence', [])
    topics = item.get('topic_keywords', [])
    ref_summary = item.get('reference_summary', "")

    if not evidence: return None

    current_feedback = None
    final_output = None
    loop_count = 0

    for loop in range(2):
        loop_count = loop + 1
        draft_json = generate_draft(evidence, topics, current_feedback)
        if not draft_json: break

        is_pass, feedback = evaluate_summary(draft_json, evidence, topics)
        final_output = draft_json
        if is_pass:
            break
        else:
            current_feedback = feedback

    # 结果封装
    final_text = ""
    if final_output:
        try:
            final_obj = json.loads(final_output)
            final_text = " ".join([x['text'] for x in final_obj])
        except:
            final_text = str(final_output)

    return {
        "id": sample_id,
        "ref_summary": ref_summary,
        "gen_summary": final_text,
        "raw_json": final_output,
        "loops": loop_count
    }


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ 找不到 {INPUT_FILE}")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    results = []
    completed_ids = set()
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            try:
                results = json.load(f)
                completed_ids = {item['id'] for item in results}
            except:
                pass

    tasks = [item for item in dataset if item['id'] not in completed_ids]
    print(f"🚀 火力全开模式: {MAX_WORKERS} 线程 | 待处理: {len(tasks)}")

    # 计数器
    processed_count = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # 建立 Future 到原始 Item 的映射，方便我们取回原文
        future_to_item = {executor.submit(process_single_sample, item): item for item in tasks}

        for future in tqdm(as_completed(future_to_item), total=len(tasks), desc="Processing"):
            try:
                result = future.result()
                # 取出原始数据，为了打印原文证据
                original_item = future_to_item[future]

                if result:
                    with file_lock:
                        results.append(result)
                        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                            json.dump(results, f, ensure_ascii=False, indent=2)

                    # =========== 📊 实时日志监控 ===========
                    processed_count += 1
                    if processed_count % 10 == 0:
                        print(f"\n\n{'=' * 20} 🟢 进度检查 ({processed_count}/{len(tasks)}) {'=' * 20}")
                        print(f"📄 样本ID: {result['id']}")

                        # 打印输入的证据（取前150个字符预览，防止太长）
                        evidence_preview = " ".join(original_item.get('extracted_evidence', []))
                        print(f"📝 输入证据(Preview): {evidence_preview[:150]}...")

                        # 打印模型生成的摘要
                        print(f"🤖 生成摘要: {result['gen_summary']}")

                        # 打印修正次数
                        print(f"🔄 修正轮次: {result['loops']}")
                        print(f"{'=' * 60}\n")
                    # =======================================

            except Exception as e:
                print(f"Error: {e}")

    print(f"\n✅ 任务完成！")


if __name__ == "__main__":
    main()