import torch

print(f"PyTorch 版本: {torch.__version__}")
print(f"CUDA 是否可用: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"当前显卡: {torch.cuda.get_device_name(0)}")
    print(f"显存大小: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
else:
    print("❌ 警告: 目前是 CPU 模式，请检查安装命令。")