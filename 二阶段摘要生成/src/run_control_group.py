import json
import os
import time
import threading
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from tqdm import tqdm

# ================= 配置区域 =================
API_KEY = "sk-368e11c3ac0048f485f16ad3bfff06de"
BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-chat"  # DeepSeek V3

# 输入文件 (必须包含 extracted_evidence 字段)
INPUT_FILE = r"C:\Users\ZJH\PycharmProjects\pythonProject\二阶段摘要生成\dist\experiment_evidence_subset.json"
# 输出文件 (记录全过程数据)
OUTPUT_FILE = "experiment_results_full_pipeline.json"

# 并发数
MAX_WORKERS = 5  # 因为每个任务要调3次API，建议稍微调低并发防止限流
# ===============================================

file_lock = threading.Lock()
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


# --- 辅助函数：清洗 JSON ---
def clean_json_string(s):
    """防止 LLM 输出 Markdown 代码块包裹 JSON"""
    if not s: return ""
    s = s.strip()
    # 去掉可能的 ```json ... ```
    match = re.search(r"```json(.*?)```", s, re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r"```(.*?)```", s, re.DOTALL)
    if match:
        return match.group(1).strip()
    return s


# --- 基础 LLM 调用 ---
def call_llm(prompt, system_prompt="You are a helpful assistant.", json_mode=False):
    """统一 API 调用接口"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            kwargs = {
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
                "temperature": 0.1 if json_mode else 0.7,  # 评估时温度低一点更严谨
                "max_tokens": 1024,
                "timeout": 120
            }
            if json_mode:
                kwargs["response_format"] = {'type': 'json_object'}

            response = client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            print(f"\n⚠️ 请求遇到问题 (Attempt {attempt + 1}): {str(e)[:50]}...")
            time.sleep(2)
    return None


# ================= 核心流程函数 =================

# --- 第一步：生成初稿 (Generator) ---
def step_1_generate_draft(evidence_text):
    prompt = f"""
    You are an academic summarizer. 
    Based ONLY on the following extracted evidence sentences, write a concise and coherent summary.
    Do not add any external information.

    ### EXTRACTED EVIDENCE:
    {evidence_text}

    ### DRAFT SUMMARY:
    """
    return call_llm(prompt, system_prompt="You are a strictly evidence-based writer.")


# --- 第二步：评估初稿 (Evaluator) ---
def step_2_evaluate_draft(draft, evidence_text):
    system_prompt = """You are a strict Editor. Verify the summary against the Evidence Chain.
    Select ONE operation from:
    1. Op_supp (Supplement missing info)
    2. Op_delete (Remove hallucinations)
    3. Op_rewrite (Fix logic/ambiguity)
    4. Op_simplify (Remove redundancy)
    5. Op_retain (No changes needed)

    Output JSON format:
    {
        "score": <int 1-5>,
        "reasoning": "<step-by-step analysis>",
        "operation": "<Op_supp/Op_delete/Op_rewrite/Op_simplify/Op_retain>",
        "args": {
            "target": "<text to change>",
            "suggestion": "<new text or instruction>"
        }
    }
    """

    user_prompt = f"""
    ### EVIDENCE CHAIN:
    {evidence_text}

    ### DRAFT SUMMARY:
    {draft}

    ### TASK:
    Evaluate the draft. Return JSON.
    """

    response = call_llm(user_prompt, system_prompt, json_mode=True)

    # 尝试解析 JSON
    try:
        clean_resp = clean_json_string(response)
        return json.loads(clean_resp)
    except:
        print(f"❌ JSON 解析失败，跳过评估")
        return None


# --- 第三步：修正摘要 (Refiner) ---
def step_3_apply_revision(draft, eval_result):
    # 如果评估器觉得完美，直接返回原稿
    op = eval_result.get("operation")
    if op == "Op_retain":
        return draft

    # 否则调用 LLM 执行修改
    prompt = f"""
    You are a Revision Assistant. 
    Refine the summary based on the editor's instruction.

    ### ORIGINAL DRAFT:
    {draft}

    ### EDITOR INSTRUCTION:
    - Operation: {op}
    - Target: {eval_result['args'].get('target')}
    - Suggestion: {eval_result['args'].get('suggestion')}

    ### REFINED SUMMARY (Output only the new text):
    """
    return call_llm(prompt, system_prompt="You modify text exactly as instructed.")


# ================= 主处理逻辑 =================

def process_single_sample(item):
    """处理单个样本的全流程"""
    sample_id = item['id']

    # 1. 获取证据链 (如果是列表则拼接)
    evidence_raw = item.get('extracted_evidence', [])
    if isinstance(evidence_raw, list):
        evidence_text = " ".join(evidence_raw)
    else:
        evidence_text = str(evidence_raw)

    if not evidence_text:
        return None

    # --- Step 1: 生成初稿 ---
    initial_summary = step_1_generate_draft(evidence_text)
    if not initial_summary: return None

    # --- Step 2: 评估 ---
    eval_result = step_2_evaluate_draft(initial_summary, evidence_text)
    if not eval_result:
        # 如果评估失败，至少保存初稿
        eval_result = {"error": "JSON parse failed", "operation": "None"}
        final_summary = initial_summary
    else:
        # --- Step 3: 修正 (只有评估成功才修正) ---
        final_summary = step_3_apply_revision(initial_summary, eval_result)

    # 返回完整记录
    return {
        "id": sample_id,
        "evidence_used": evidence_text,
        "ref_summary": item.get('reference_summary', ""),

        # 核心三要素
        "initial_summary": initial_summary,  # 初稿
        "evaluation_output": eval_result,  # 评估器的 JSON
        "final_summary": final_summary if final_summary else initial_summary  # 终稿
    }


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ 找不到输入文件: {INPUT_FILE}")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    results = []
    completed_ids = set()

    # 断点续传逻辑
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
                results = existing_data
                completed_ids = {item['id'] for item in results}
                print(f"🔄 检测到存档，已跳过 {len(completed_ids)} 条")
            except:
                pass

    tasks = [item for item in dataset if item['id'] not in completed_ids]
    # tasks = tasks[:5] # 调试时可以取消注释，只跑前5条

    print(f"🚀 开始全流程实验 (Gen -> Eval -> Refine) | 待处理: {len(tasks)}")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_item = {executor.submit(process_single_sample, item): item for item in tasks}

        for future in tqdm(as_completed(future_to_item), total=len(tasks), desc="Processing"):
            try:
                result = future.result()
                if result:
                    with file_lock:
                        results.append(result)
                        # 实时保存
                        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                            json.dump(results, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"任务异常: {e}")

    print(f"\n✅ 所有流程完成！结果已保存至 {OUTPUT_FILE}")


if __name__ == "__main__":
    main()