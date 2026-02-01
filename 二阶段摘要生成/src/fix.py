import json
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from tqdm import tqdm

# ================= 配置 =================
API_KEY = "sk-368e11c3ac0048f485f16ad3bfff06de"
BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-chat"

# 指向你已经生成了 300 条（含空值）的文件
TARGET_FILE = r"C:\Users\ZJH\PycharmProjects\pythonProject\二阶段摘要生成\dist\final_experiment_results_aggressive.json"
# 原始输入文件，用于找回 evidence
INPUT_SOURCE = r"C:\Users\ZJH\PycharmProjects\pythonProject\二阶段摘要生成\dist\experiment_evidence_subset.json"

MAX_WORKERS = 3  # 补漏不用太快，稳一点
# =======================================

file_lock = threading.Lock()
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# 加载评估模型 (既然要补漏，评估还是要开的)
print("正在加载评估模型...")
try:
    embedder = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')
    nli_model = pipeline("text-classification", model='roberta-large-mnli', device=0)
    print("✅ 模型加载完毕")
except:
    print("⚠️ 模型加载失败，将盲跑")
    embedder = None
    nli_model = None


def call_llm_robust(prompt, system_prompt="You are a helpful assistant."):
    """
    更顽强的调用函数：重试 5 次，等待时间更长
    """
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                stream=False,
                temperature=0.3,
                max_tokens=1024,
                timeout=600
            )
            content = response.choices[0].message.content
            if content: return content
        except Exception as e:
            print(f"⚠️ [Retry {attempt + 1}] API Error: {str(e)[:50]}...")
            time.sleep(5)  # 歇久一点
    return None


def generate_draft(evidence_list, topic_keywords, feedback=None):
    evidence_text = "\n".join([f"[ID:{i}] {sent}" for i, sent in enumerate(evidence_list)])
    topics_text = ", ".join(topic_keywords)
    prompt = f"""
    You are an academic summarization expert.
    ### INPUT DATA
    TOPIC KEYWORDS: {topics_text}
    EXTRACTED EVIDENCE:
    {evidence_text}
    ### REQUIREMENTS
    1. Faithfulness: Based strictly on Evidence.
    2. Citation: Include citation IDs.
    3. Format: JSON list of objects with "text" and "citations".
    ### FEEDBACK
    {feedback if feedback else "None"}
    Output ONLY JSON:
    """
    content = call_llm_robust(prompt, system_prompt="You are a JSON generator.")
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


def repair_item(item, source_map):
    s_id = item['id']
    # 从原始文件找回输入数据
    if s_id not in source_map:
        print(f"❌ 找不到原始数据 ID: {s_id}")
        return None

    source_item = source_map[s_id]
    evidence = source_item.get('extracted_evidence', [])
    topics = source_item.get('topic_keywords', [])

    if not evidence: return item  # 没救了

    current_feedback = None
    final_output = None

    # 跑流程
    for loop in range(2):
        draft_json = generate_draft(evidence, topics, current_feedback)
        if not draft_json: continue  # 就算失败也继续试

        is_pass, feedback = evaluate_summary(draft_json, evidence, topics)
        final_output = draft_json
        if is_pass:
            break
        else:
            current_feedback = feedback

    # 更新结果
    if final_output:
        try:
            final_obj = json.loads(final_output)
            final_text = " ".join([x['text'] for x in final_obj])
            item['gen_summary'] = final_text
            item['raw_json'] = final_output
            item['loops'] = loop + 1
            return item
        except:
            pass

    return None  # 依然失败


def main():
    # 1. 读取现有结果
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        results = json.load(f)

    # 2. 读取原始输入 (为了拿 evidence)
    with open(INPUT_SOURCE, 'r', encoding='utf-8') as f:
        source_data = json.load(f)
        source_map = {item['id']: item for item in source_data}

    # 3. 找出空样本
    empty_items = []
    for item in results:
        gen = item.get('gen_summary', "")
        if not gen or len(str(gen).strip()) < 5:
            empty_items.append(item)

    print(f"🔍 发现 {len(empty_items)} 个空样本，开始修复...")

    if len(empty_items) == 0:
        print("🎉 没有空样本，无需修复！")
        return

    # 4. 开始修复
    fixed_count = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_item = {executor.submit(repair_item, item, source_map): item for item in empty_items}

        for future in tqdm(as_completed(future_to_item), total=len(empty_items)):
            try:
                new_item = future.result()
                if new_item:
                    # 更新内存中的结果列表
                    for idx, res in enumerate(results):
                        if res['id'] == new_item['id']:
                            results[idx] = new_item
                            break

                    # 实时回写文件 (防止再次中断)
                    with file_lock:
                        with open(TARGET_FILE, 'w', encoding='utf-8') as f:
                            json.dump(results, f, ensure_ascii=False, indent=2)
                    fixed_count += 1
            except Exception as e:
                print(f"修复出错: {e}")

    print(f"✅ 修复完成！成功挽救了 {fixed_count}/{len(empty_items)} 个样本。")


if __name__ == "__main__":
    main()