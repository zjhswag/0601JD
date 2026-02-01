import json
import os
import re
import numpy as np
import torch
from rouge_score import rouge_scorer
from bert_score import score as bert_score_func

# ================= 配置 =================
# 指向你的原始数据文件
RESULTS_FILE = r"C:\Users\ZJH\PycharmProjects\pythonProject\二阶段摘要生成\dist\experiment_evidence_subset.json"
# =======================================

REMAP = {
    "-lrb-": "(", "-rrb-": ")", "-lcb-": "{", "-rcb-": "}",
    "-lsb-": "[", "-rsb-": "]", "``": '"', "''": '"'
}


def clean_text(text):
    if not text:
        return ""
    text = str(text)
    text = text.replace("<q>", " ")
    pattern = re.compile("|".join(re.escape(k) for k in REMAP.keys()))
    text = pattern.sub(lambda m: REMAP[m.group(0)], text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def calculate_bertsum_metrics(results_file):
    if not os.path.exists(results_file):
        print(f"Error: {results_file} not found.")
        return

    print(f"Loading data from: {results_file}")
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # === 打印预览 (调试用) ===
    print(f"总数据量: {len(data)}")
    if len(data) > 0:
        item = data[0]
        # 调试打印，确保取到了值
        print(f"🔍 调试 Key Check: 'reference_summary' in keys? {'reference_summary' in item}")
        print(f"【Ref Preview】: {str(item.get('reference_summary', ''))[:50]}...")
    print(f"{'=' * 50}\n")
    # ===========================

    print(f"Calculating metrics for {len(data)} samples...")

    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

    rouge1_scores = []
    rouge2_scores = []
    rougeL_scores = []

    refs = []
    cands = []

    for item in data:
        # 🔥🔥🔥 修正点：这里改成了 'reference_summary' 🔥🔥🔥
        ref = clean_text(item.get('reference_summary', ""))

        raw_evidence = item.get('extracted_evidence', [])
        if isinstance(raw_evidence, list):
            gen_raw = " ".join(raw_evidence)
        else:
            gen_raw = str(raw_evidence)
        gen = clean_text(gen_raw)

        # 再次防止空跑
        if not ref:
            continue  # 如果 Reference 本身就是空的，跳过

        if not gen:
            gen = "empty"

        scores = scorer.score(ref, gen)
        rouge1_scores.append(scores['rouge1'].fmeasure)
        rouge2_scores.append(scores['rouge2'].fmeasure)
        rougeL_scores.append(scores['rougeL'].fmeasure)

        refs.append(ref)
        cands.append(gen)

    print("-" * 30)
    # 防止分母为0
    if len(rouge1_scores) > 0:
        print(f"BERTSum (Extraction) ROUGE-1 F1: {np.mean(rouge1_scores) * 100:.2f}")
        print(f"BERTSum (Extraction) ROUGE-2 F1: {np.mean(rouge2_scores) * 100:.2f}")
        print(f"BERTSum (Extraction) ROUGE-L F1: {np.mean(rougeL_scores) * 100:.2f}")
    else:
        print("所有样本均无效！")
    print("-" * 30)

    print("Calculating BERTScore (this may take a while)...")
    try:
        if len(cands) > 0:
            P, R, F1 = bert_score_func(
                cands,
                refs,
                lang="en",
                verbose=True,
                batch_size=32,
                model_type="distilbert-base-uncased"
            )
            print("-" * 30)
            print(f"BERTSum (Extraction) BERTScore F1: {F1.mean().item() * 100:.2f}")
            print("-" * 30)
        else:
            print("没有有效样本进行 BERTScore 计算")
    except Exception as e:
        print(f"BERTScore calculation failed: {e}")


if __name__ == "__main__":
    calculate_bertsum_metrics(RESULTS_FILE)