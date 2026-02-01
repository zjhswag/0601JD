import matplotlib.pyplot as plt

# --- 修正点：更改样式名称 ---
try:
    plt.style.use('seaborn-whitegrid')
except:
    plt.style.use('ggplot')

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 数据
labels = ['Full Document', 'Evidence Chain (Ours)']
tokens = [845, 210] # 假设的平均长度
rouge_scores = [40.42, 41.38] # 对应的 R-1 分数

x = range(len(labels))
width = 0.35

fig, ax1 = plt.subplots(figsize=(7, 5))

# 柱状图：Token 数量
bars = ax1.bar(x, tokens, width, label='Avg. Input Tokens', color='lightgray', edgecolor='black')
ax1.set_ylabel('Token Count', fontsize=12)
ax1.set_xticks(x)
ax1.set_xticklabels(labels, fontsize=11)
ax1.bar_label(bars, padding=3)

# 折线图：ROUGE 分数
ax2 = ax1.twinx()
ax2.plot(x, rouge_scores, color='red', marker='D', markersize=8, linewidth=2, label='ROUGE-1 Score')
ax2.set_ylabel('ROUGE-1 Score', color='red', fontsize=12)
ax2.tick_params(axis='y', labelcolor='red')

plt.title('Information Density Analysis: Tokens vs. Performance', fontsize=14)
plt.tight_layout()
# plt.savefig('token_efficiency.pdf')
plt.show()