import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 1. 准备数据 (替换为你模型中提取的 Attention Matrix)
# 假设原文有 10 个句子，我们需要看 CLS token 对这 10 个句子的关注度
sentences = [
    "S1: Intro...", "S2: Background...", "S3: Topic Word A...",
    "S4: Detail...", "S5: Noise...", "S6: Topic Word B...",
    "S7: Detail...", "S8: Conclusion...", "S9: Noise...", "S10: Future..."
]
# 假设 S3 和 S6 是包含主题词的关键句
# Baseline 可能会关注位置靠前的 S1, S2 (Lead-3 偏见)
attn_baseline = np.array([[0.3, 0.25, 0.1, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05]])
# Ours 应该重点关注 S3, S6, S8 (主题偏置生效)
attn_ours = np.array([[0.05, 0.05, 0.35, 0.05, 0.02, 0.30, 0.03, 0.10, 0.02, 0.03]])

def plot_heatmap(data, y_labels, title, filename):
    plt.figure(figsize=(8, 2)) # 长条形，因为只看一个 Query 对所有 Key 的关注
    sns.heatmap(
        data,
        annot=True, # 显示数值
        fmt=".2f",
        xticklabels=y_labels,
        yticklabels=["[CLS]"], # 或者 "Summary Token"
        cmap="Blues", # 颜色风格：Reds, Blues, YlGnBu
        cbar=False
    )
    plt.title(title)
    plt.xticks(rotation=45, ha='right')
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.show()

plot_heatmap(attn_baseline, sentences, "Baseline Attention Distribution", "attn_base.pdf")
plot_heatmap(attn_ours, sentences, "Ours (Topic-Biased) Attention Distribution", "attn_ours.pdf")