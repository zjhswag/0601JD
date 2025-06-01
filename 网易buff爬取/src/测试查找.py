import json
import os
import time
# 指定包含 JSON 文件的目录
json_dir = os.path.join(os.path.dirname(__file__), '..', 'dist')

# 合并所有 JSON 文件内容的字典
merged_data = {}

# 遍历目录中的所有 JSON 文件
for filename in os.listdir(json_dir):
    if filename.endswith('.json'):
        file_path = os.path.join(json_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 将每个文件中的内容合并到一个字典中
            merged_data.update(data)

# 将合并后的字典保存到一个新的 JSON 文件中
merged_file_path = os.path.join(json_dir, 'merged_data.json')
with open(merged_file_path, 'w', encoding='utf-8') as f:
    json.dump(merged_data, f, ensure_ascii=False, indent=4)

# print(f'所有 JSON 文件已合并并保存到 {merged_file_path}')
# print(merged_file_path)
f1 = time.time()*1000
paint_wear = float(merged_data.get("M249（StatTrak™） | 闹市区 (崭新出厂)"))
f2 = time.time()*1000
print("耗费多少",f2-f1,"ms")
print(paint_wear)
