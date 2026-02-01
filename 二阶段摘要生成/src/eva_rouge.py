import json
import os
import re
import numpy as np
import torch
from rouge_score import rouge_scorer
from bert_score import score as bert_score_func

# ================= 配置 =================
# 根据你想测哪个文件，取消注释对应行
RESULTS_FILE = r"C:\Users\ZJH\PycharmProjects\pythonProject\二阶段摘要生成\dist\control_group_results.json"
# RESULTS_FILE = r"C:\Users\ZJH\PycharmProjects\pythonProject\二阶段摘要生成\dist\final_experiment_results_aggressive.json"
# RESULTS_FILE = r"C:\Users\ZJH\PycharmProjects\pythonProject\二阶段摘要生成\dist\final_experiment_results_aggressive.json"
# =======================================

# 特殊字符映射表 (用于清洗数据集中的奇怪符号)
REMAP = {
    "-lrb-": "(", "-rrb-": ")", "-lcb-": "{", "-rcb-": "}",
    "-lsb-": "[", "-rsb-": "]", "``": '"', "''": '"'
}


def clean_text(text):
    """
    关键清洗函数：处理 <q> 标签和特殊符号
    """
    if not text:
        return ""
    text = str(text)

    # 1. 处理 <q> 标签：在 CNNDM 数据集中，<q> 代表句子分隔
    # 替换为空格，避免单词粘连 (例如 end<q>Start -> end Start)
    text = text.replace("<q>", " ")

    # 2. 替换 PTB Tokenization 的转义字符
    # 很多数据集里括号是 -lrb-，必须转回来，否则影响 BERTScore 和 ROUGE
    pattern = re.compile("|".join(re.escape(k) for k in REMAP.keys()))
    text = pattern.sub(lambda m: REMAP[m.group(0)], text)

    # 3. 移除多余的空白字符 (换行符转空格，多个空格转一个)
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def calculate_metrics(results_file):
    if not os.path.exists(results_file):
        print(f"Error: {results_file} not found.")
        return

    print("Loading results...")
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # === 打印预览 (带清洗效果) ===
    print(f"总数据量: {len(data)}")
    for i in range(min(3, len(data))):
        item = data[i]
        print(f"\n{'=' * 20} Sample {i} (Preview) {'=' * 20}")
        print(f"【Ref (Raw)】: {item.get('ref_summary', '')[:100]}...")
        print(f"【Ref (Clean)】: {clean_text(item.get('ref_summary', ''))[:100]}...")
        print(f"【Gen (Clean)】: {clean_text(item.get('gen_summary', ''))[:100]}...")
    print(f"{'=' * 50}\n")
    # ===========================

    print(f"Calculating metrics for {len(data)} samples...")

    # 1. 初始化 ROUGE 打分器 (必须开启 use_stemmer=True)
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

    rouge1_scores = []
    rouge2_scores = []
    rougeL_scores = []

    refs = []
    cands = []
    empty_count = 0

    for item in data:
        # 核心步骤：清洗文本
        ref = clean_text(item.get('ref_summary', ""))
        gen = clean_text(item.get('gen_summary', ""))

        # 空值检测
        if not gen or len(gen) < 2:
            empty_count += 1
            gen = "empty_generation"  # 占位，防止报错，分数为0

        # ROUGE 计算
        scores = scorer.score(ref, gen)
        rouge1_scores.append(scores['rouge1'].fmeasure)
        rouge2_scores.append(scores['rouge2'].fmeasure)
        rougeL_scores.append(scores['rougeL'].fmeasure)

        refs.append(ref)
        cands.append(gen)

    if empty_count > 0:
        print(f"⚠️ 警告: 发现 {empty_count} 个空摘要 (占比 {empty_count / len(data):.1%})，这会拉低平均分！")

    print("-" * 30)
    print(f"ROUGE-1 F1: {np.mean(rouge1_scores) * 100:.2f}")
    print(f"ROUGE-2 F1: {np.mean(rouge2_scores) * 100:.2f}")
    print(f"ROUGE-L F1: {np.mean(rougeL_scores) * 100:.2f}")
    print("-" * 30)

    # 2. 计算 BERTScore
    print("Calculating BERTScore (this may take a while)...")
    try:
        # device = 'cuda' if torch.cuda.is_available() else 'cpu'

        # 说明：
        # distilbert-base-uncased: 速度快，分数通常偏高 (80-90)
        # roberta-large: 速度慢，更准确，论文标准 (通常分数略低一点)
        # 如果你想跑得快，保持下面这行；如果你想写论文更严谨，删掉 model_type 参数让它默认用 roberta

        P, R, F1 = bert_score_func(
            cands,
            refs,
            lang="en",
            verbose=True,
            batch_size=32,
            model_type="distilbert-base-uncased"
        )

        print("-" * 30)
        print(f"BERTScore F1: {F1.mean().item() * 100:.2f}")
        print("-" * 30)
    except Exception as e:
        print(f"BERTScore calculation failed: {e}")


if __name__ == "__main__":
    calculate_metrics(RESULTS_FILE)