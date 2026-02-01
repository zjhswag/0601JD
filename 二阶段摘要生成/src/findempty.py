import json
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from tqdm import tqdm

# ================= 配置 =================
API_KEY = "sk-368e11c3ac0048f485f16ad3bfff06de"
BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-chat"

# 文件路径
TARGET_FILE = r"C:\Users\ZJH\PycharmProjects\pythonProject\二阶段摘要生成\dist\final_experiment_results_aggressive.json"
INPUT_SOURCE = r"C:\Users\ZJH\PycharmProjects\pythonProject\二阶段摘要生成\dist\experiment_evidence_subset.json"

MAX_WORKERS = 1  # 设为1，我们要看看到底是谁在报错
# =======================================

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
file_lock = threading.Lock()


def call_llm_robust(prompt, system_prompt="You are a helpful assistant."):
    max_retries = 3
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
                timeout=30  # 超时改短点，快速失败
            )
            content = response.choices[0].message.content
            if content: return content
        except Exception as e:
            print(f"  API Error: {str(e)[:50]}...")
            time.sleep(1)
    return None


def repair_item(item, source_map):
    s_id = item['id']

    # 1. 检查原始数据
    if s_id not in source_map:
        print(f"❌ [ID:{s_id}] 原始数据丢失！")
        return None

    source_item = source_map[s_id]
    evidence = source_item.get('extracted_evidence', [])
    topics = source_item.get('topic_keywords', [])

    # 2. 打印侦探日志！
    print(f"\n🕵️‍♂️ 正在调查 [ID:{s_id}]")
    print(f"   - 证据数量: {len(evidence)}")
    print(f"   - 证据内容预览: {str(evidence)[:100]}...")

    if not evidence:
        print(f"   ⚠️ [ID:{s_id}] 证据为空！无法生成！使用占位符填充。")
        item['gen_summary'] = "Summary unavailable due to empty evidence."
        return item

    # 3. 尝试最后一次生成
    evidence_text = "\n".join([f"[ID:{i}] {sent}" for i, sent in enumerate(evidence)])
    prompt = f"""Summarize based on evidence:\n{evidence_text}\nOutput JSON with 'text' field."""

    content = call_llm_robust(prompt)

    # 4. 强制修复逻辑
    final_text = ""
    if content:
        try:
            # 尝试解析 JSON
            if "```" in content:
                content = content.replace("```json", "").replace("```", "").strip()
            data = json.loads(content)
            if isinstance(data, list):
                final_text = " ".join([x.get('text', '') for x in data])
            elif isinstance(data, dict):
                final_text = data.get('text', '')
        except:
            # 解析失败，直接用原始内容
            final_text = content

    # 5. 无论如何都要填点东西进去！
    if not final_text or len(final_text) < 5:
        print(f"   ❌ [ID:{s_id}] 生成依然失败或为空。强制使用占位符。")
        final_text = "Generation failed after multiple retries."
    else:
        print(f"   ✅ [ID:{s_id}] 修复成功！")

    item['gen_summary'] = final_text
    # 随便填个假 JSON 结构防止评估代码报错
    item['raw_json'] = json.dumps([{"text": final_text, "citations": []}])
    item['loops'] = 99  # 标记一下这是强制修复的

    return item


def main():
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        results = json.load(f)

    with open(INPUT_SOURCE, 'r', encoding='utf-8') as f:
        source_data = json.load(f)
        source_map = {item['id']: item for item in source_data}

    # 找出空样本
    empty_items = []
    for item in results:
        gen = item.get('gen_summary', "")
        if not gen or len(str(gen).strip()) < 5:
            empty_items.append(item)

    print(f"🔍 锁定 {len(empty_items)} 个顽固样本...")

    if len(empty_items) == 0:
        print("🎉 没有空样本了！")
        return

    # 这里的关键是：必须把修复后的结果写回去，即使生成失败了也要写个占位符
    for item in empty_items:
        new_item = repair_item(item, source_map)
        if new_item:
            # 更新列表
            for idx, res in enumerate(results):
                if res['id'] == new_item['id']:
                    results[idx] = new_item
                    break

    # 最后统一保存一次
    print("💾 正在保存强制修复结果...")
    with open(TARGET_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("✅ 所有空洞已强制填充完毕。")


if __name__ == "__main__":
    main()