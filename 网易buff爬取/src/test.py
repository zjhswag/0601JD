import numpy as np
import matplotlib.pyplot as plt

# 1. 加载文件
# 推荐写法
file_path = r'C:\Users\ZJH\Desktop\BertSum-master\results\loss_data.npz'
# file_path = 'C:\Users\ZJH\Desktop\BertSum-master\results\loss_data.npz'  # 确保路径正确
data = np.load(file_path)

# 2. 查看里面有哪些键（Key）
# 根据你之前的 Trainer 代码，这里应该有 'train_steps', 'train_losses', 'valid_losses'
print("文件中包含的 Keys:", data.files)

# 3. 提取数据
train_steps = data['train_steps']
train_losses = data['train_losses']
print(len(train_losses))
# 如果有验证集数据，也可以提取
if 'valid_losses' in data:
    valid_losses = data['valid_losses']
    print(f"验证集数据点数量: {len(valid_losses)}")

# 4. 打印前几个和后几个数据点看看
print(f"总步数: {len(train_steps)}")
print(f"初始 Loss: {train_losses[0]}")
print(f"最终 Loss: {train_losses[-1]}")

# 5. (可选) 如果你想自己重新画图
plt.figure(figsize=(6, 4))
plt.plot(train_steps, train_losses, label='Training Loss')
# plt.plot(train_steps[:len(valid_losses)], valid_losses, label='Validation Loss') # 如果有验证集
plt.title('Training Loss Analysis')
plt.xlabel('Steps')
plt.ylabel('Loss')
plt.grid(True)
plt.legend()
plt.show()