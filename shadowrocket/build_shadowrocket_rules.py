#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Shadowrocket 规则构建主脚本
整合所有功能，生成完整的 Shadowrocket 规则文件
"""

import os
import sys
import time
import subprocess
from pathlib import Path


def run_script(script_name, description):
    """运行指定的脚本"""
    print(f"\n=== {description} ===")
    try:
        # 切换到 shadowrocket 目录运行脚本
        script_path = Path(__file__).parent / script_name
        result = subprocess.run([sys.executable, str(script_path)], 
                              capture_output=True, text=True, cwd=Path(__file__).parent)
        if result.returncode == 0:
            print(result.stdout)
            print(f"✅ {description} 完成")
        else:
            print(f"❌ {description} 失败:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ 运行 {script_name} 时出错: {e}")
        return False
    return True


def ensure_directory():
    """确保输出目录存在"""
    output_dir = Path('resultant')
    output_dir.mkdir(exist_ok=True)
    print(f'输出目录: {output_dir.absolute()}')


def print_summary():
    """打印构建摘要"""
    print('\n' + '='*60)
    print('📊 构建摘要')
    print('='*60)
    
    # 检查生成的文件
    resultant_dir = Path(__file__).parent / 'resultant'
    files_info = [
        ('cn_ip.list', '中国大陆 IP 段'),
        ('ad.list', '广告过滤域名'),
        ('Shadowrocket_gfwlist.conf', 'Shadowrocket GFWList 规则'),
        ('Shadowrocket_gfwlist.txt', 'Shadowrocket GFWList 文本'),
        ('Shadowrocket_gfwlist_ad.conf', 'Shadowrocket GFWList + 广告过滤规则'),
    ]
    
    for filename, description in files_info:
        file_path = resultant_dir / filename
        if file_path.exists():
            size = file_path.stat().st_size
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
            print(f"✅ {description} - {size:,} 字节, {lines:,} 行")
        else:
            print(f"❌ {description} - 文件不存在")


def main():
    """主函数"""
    print('🚀 开始构建 Shadowrocket 规则')
    print(f'构建时间: {time.strftime("%Y-%m-%d %H:%M:%S")}')
    
    # 确保输出目录存在
    ensure_directory()
    
    # 获取脚本目录
    script_dir = Path(__file__).parent
    
    # 构建步骤
    steps = [
        (script_dir / 'fetch_cn_ip.py', '获取中国大陆 IP 段数据'),
        (script_dir / 'fetch_ad_rules.py', '获取广告过滤规则'),
        (script_dir / 'convert_gfwlist.py', '生成 Shadowrocket GFWList 规则'),
        (script_dir / 'convert_gfwlist_ad.py', '生成 Shadowrocket GFWList + 广告过滤规则'),
    ]
    
    success_count = 0
    total_steps = len(steps)
    
    # 执行所有步骤
    for script_path, description in steps:
        if run_script(script_path, description):
            success_count += 1
        else:
            print(f'⚠️  步骤失败，但继续执行后续步骤...')
    
    # 打印构建摘要
    print_summary()
    
    # 打印最终结果
    print('='*60)
    if success_count == total_steps:
        print('🎉 所有步骤执行成功！')
        print('\n📁 生成的文件位于 resultant/ 目录：')
        print('   • Shadowrocket_gfwlist.conf - GFWList 规则')
        print('   • Shadowrocket_gfwlist_ad.conf - GFWList + 广告过滤规则')
        print('\n📖 使用方法：')
        print('   1. 将 .conf 文件导入到 Shadowrocket 应用中')
        print('   2. 在 Shadowrocket 中选择对应的配置文件')
        print('   3. 启用代理即可使用')
    else:
        print(f'⚠️  部分步骤失败 ({success_count}/{total_steps} 成功)')
        print('请检查上述错误信息并重新运行')
        sys.exit(1)


if __name__ == '__main__':
    main()
