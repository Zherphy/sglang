#!/usr/bin/env python3
import yaml
import sys

def validate_yaml(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            data = yaml.safe_load(content)
            print(f"✅ YAML格式正确: {file_path}")
            return True
    except yaml.YAMLError as e:
        print(f"❌ YAML格式错误: {file_path}")
        print(f"错误信息: {e}")
        if hasattr(e, 'problem_mark'):
            mark = e.problem_mark
            print(f"错误位置: 第{mark.line+1}行, 第{mark.column+1}列")
            
            # 显示错误行附近的上下文
            lines = content.split('\n')
            start = max(0, mark.line - 3)
            end = min(len(lines), mark.line + 4)
            print("\n错误上下文:")
            for i in range(start, end):
                prefix = ">>> " if i == mark.line else "    "
                print(f"{prefix}{i+1}: {lines[i]}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        validate_yaml(sys.argv[1])
    else:
        print("使用方法: python validate_yaml.py <yaml文件路径>")