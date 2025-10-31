#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
获取中国大陆 IP 段数据
数据来源：https://ispip.clang.cn/all_cn.html
"""

import time
import requests
import re
import sys
from bs4 import BeautifulSoup


def get_cn_ip_ranges():
    """获取中国大陆 IP 段列表"""
    url = 'https://ispip.clang.cn/all_cn.html'
    
    success = False
    try_times = 0
    r = None
    
    print(f'正在获取中国大陆 IP 段数据: {url}')
    
    while try_times < 5 and not success:
        try:
            r = requests.get(url, timeout=30)
            if r.status_code != 200:
                time.sleep(2)
                try_times += 1
                print(f'请求失败，重试第 {try_times} 次...')
            else:
                success = True
                break
        except Exception as e:
            print(f'请求异常: {e}')
            time.sleep(2)
            try_times += 1

    if not success:
        raise Exception(f'获取 IP 段数据失败，状态码: {r.status_code if r else "无响应"}')

    # 解析 HTML 内容
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # 查找包含 IP 段的文本内容
    ip_ranges = []
    
    # 尝试从页面文本中提取 IP 段
    text_content = soup.get_text()
    
    # 使用正则表达式匹配 CIDR 格式的 IP 段
    cidr_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}/[0-9]{1,2}\b'
    matches = re.findall(cidr_pattern, text_content)
    
    for match in matches:
        # 验证 IP 段格式
        if validate_cidr(match):
            ip_ranges.append(match)
    
    # 去重并排序
    ip_ranges = list(set(ip_ranges))
    ip_ranges.sort()
    
    print(f'成功获取 {len(ip_ranges)} 个中国大陆 IP 段')
    return ip_ranges


def validate_cidr(cidr):
    """验证 CIDR 格式的 IP 段"""
    try:
        ip, prefix = cidr.split('/')
        
        # 验证 IP 地址
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        
        for part in parts:
            if not (0 <= int(part) <= 255):
                return False
        
        # 验证前缀长度
        if not (0 <= int(prefix) <= 32):
            return False
        
        return True
    except:
        return False


def save_cn_ip_list(ip_ranges, output_file='resultant/cn_ip.list'):
    """保存中国大陆 IP 段列表"""
    import os
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f'# 中国大陆 IP 段列表\n')
        f.write(f'# 数据来源: https://ispip.clang.cn/all_cn.html\n')
        f.write(f'# 更新时间: {time.strftime("%Y-%m-%d %H:%M:%S")}\n')
        f.write(f'# 共计 {len(ip_ranges)} 个 IP 段\n\n')
        
        for ip_range in ip_ranges:
            f.write(f'{ip_range}\n')
    
    print(f'中国大陆 IP 段列表已保存到: {output_file}')


if __name__ == '__main__':
    try:
        # 获取中国大陆 IP 段
        ip_ranges = get_cn_ip_ranges()
        
        if not ip_ranges:
            print('警告: 未获取到任何 IP 段数据')
            sys.exit(1)
        
        # 保存到文件
        save_cn_ip_list(ip_ranges)
        
        print('中国大陆 IP 段数据获取完成')
        
    except Exception as e:
        print(f'错误: {e}')
        sys.exit(1)