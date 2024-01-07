import json
import argparse

# 创建解析器并添加参数
parser = argparse.ArgumentParser()
parser.add_argument('-b', '--batch_size', type=int, required=True, help='Batch size to set')
args = parser.parse_args()

# 读取json文件
with open('config.json', 'r') as file:
    data = json.load(file)

data = json.loads(json.dumps(data).replace('false', 'False').replace('true', 'True'))

# 修改batch_size的值
data['train']['batch_size'] = args.batch_size

data = json.loads(json.dumps(data).replace('False', 'false').replace('True', 'true'))
# 将修改后的数据写回文件
with open('config.json', 'w') as file:
    json.dump(data, file, indent=2)