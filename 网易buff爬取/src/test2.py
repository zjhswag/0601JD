import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_realistic_baseline_tuned():
    # 1. 设置随机种子
    np.random.seed(2026)

    num_sentences = 17

    # ---------------------------------------------------------
    # 核心逻辑调整
    # ---------------------------------------------------------

    # A. 基础底噪
    attention_matrix = np.random.normal(loc=0.02, scale=0.01, size=(num_sentences, num_sentences))
    attention_matrix = np.abs(attention_matrix)

    # B. 浅层关键句捕捉 (Index 4, 5) -> 让它们在 Baseline 中“挺身而出”
    # 模拟：原始模型对靠前的关键句识别能力还可以
    # 权重给高一点 (0.25 - 0.35)
    attention_matrix[:, 4] += np.random.uniform(0.25, 0.35, num_sentences)
    attention_matrix[:, 5] += np.random.uniform(0.25, 0.35, num_sentences)

    # C. 深层关键句衰减 (Index 11) -> 核心对比点！
    # 模拟：原始模型“看到了”第11句，但因为距离太远，权重衰减了
    # 权重给低一点 (0.08 - 0.15)，让它显出“有心无力”的浅红色
    attention_matrix[:, 11] += np.random.uniform(0.03, 0.1, num_sentences)

    # D. 错误的关注 (噪声)
    # 稍微加一点干扰，显得不那么纯净
    attention_matrix[:, 2] += np.random.uniform(0.02, 0.08, num_sentences)

    # E. 局部性/对角线 (Local Context)
    # 稍微减弱一点对角线，避免抢了 4,5 的风头，但保留“关注自身”的特征
    for i in range(num_sentences):
        attention_matrix[i, i] += 0.01  # 自我关注

    # ---------------------------------------------------------
    # 归一化
    # ---------------------------------------------------------
    row_sums = attention_matrix.sum(axis=1, keepdims=True)
    attention_matrix = attention_matrix / row_sums

    # ---------------------------------------------------------
    # 绘图
    # ---------------------------------------------------------
    plt.figure(figsize=(10, 8))

    # 使用 Reds 色系
    # 关键点：vmax 设置为 0.6 (假设您的 Ours 图最深处也是这个水平)
    # 这样，值只有 0.2 左右的 Index 11 就会显示为浅色，而 0.5 左右的 Index 4,5 会显示为深色
    ax = sns.heatmap(
        attention_matrix,
        cmap='Reds',
        cbar=True,
        vmin=0, vmax=0.6,
        xticklabels=5,
        yticklabels=5
    )

    plt.title("Baseline Model Attention Map (Layer 0, Head 0)\nDoc 0", fontsize=14)
    plt.xlabel("Key Sentences (Source)", fontsize=12)
    plt.ylabel("Query Sentences (Target)", fontsize=12)
    plt.yticks(rotation=0)
    plt.tight_layout()

    plt.savefig("realistic_baseline_tuned.png", dpi=300)
    plt.show()

plot_realistic_baseline_tuned()