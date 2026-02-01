import matplotlib.pyplot as plt
import numpy as np

# --- 修正点：更改样式名称以兼容旧版本 ---
try:
    plt.style.use('seaborn-whitegrid') # 尝试使用通用seaborn样式
except:
    plt.style.use('ggplot') # 如果还报错，则回退到ggplot样式

plt.rcParams['font.sans-serif'] = ['SimHei'] # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
plt.rcParams['font.family'] = 'sans-serif'  # 确保字体设置生效

# 模拟数据：迭代 0 到 3 轮
rounds = [0, 1, 2, 3]
rouge_scores = [41.38, 41.10, 40.85, 40.60] # ROUGE 逐渐微降
geval_scores = [4.21, 4.55, 4.68, 4.69]     # G-Eval 逐渐上升并收敛

fig, ax1 = plt.subplots(figsize=(8, 5))

# 绘制左轴 (ROUGE)
color = 'tab:blue'
ax1.set_xlabel('Iteration Round ($t$)', fontsize=12)
ax1.set_ylabel('ROUGE-1 Score', color=color, fontsize=12)
ax1.plot(rounds, rouge_scores, color=color, marker='o', linestyle='--', linewidth=2, label='ROUGE-1')
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_xticks(rounds)

# 绘制右轴 (G-Eval)
ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('G-Eval Score', color=color, fontsize=12)
ax2.plot(rounds, geval_scores, color=color, marker='s', linestyle='-', linewidth=2, label='G-Eval')
ax2.tick_params(axis='y', labelcolor=color)

# 添加图例
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='center right')

plt.title('Performance Trajectory across Iteration Rounds', fontsize=14)
plt.tight_layout()
# plt.savefig('iteration_convergence.pdf') # 如果需要保存PDF取消注释
plt.show()