#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
获取广告过滤规则
参考 Shadowrocket-ADBlock-Rules-Forever 项目的 ad.py
"""

import time
import requests
import re
import sys
from urllib.parse import urlparse


def get_rule(url):
    """获取规则内容"""
    success = False
    try_times = 0
    r = None
    
    print(f'正在获取规则: {url}')
    
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
        raise Exception(f'获取规则失败: {url}，状态码: {r.status_code if r else "无响应"}')

    return r.text


def clear_rule(rule_text):
    """清理规则格式"""
    lines = rule_text.split('\n')
    cleared_lines = []
    
    for line in lines:
        line = line.strip()
        
        # 跳过空行和注释
        if not line or line.startswith('#') or line.startswith('!'):
            continue
        
        # 跳过特殊格式的规则
        if line.startswith('@@') or '##' in line or '#@#' in line:
            continue
        
        # 处理 ||domain^ 格式
        if line.startswith('||') and line.endswith('^'):
            domain = line[2:-1]
            if is_valid_domain(domain):
                cleared_lines.append(domain)
        
        # 处理 |http://domain 格式
        elif line.startswith('|http://') or line.startswith('|https://'):
            try:
                parsed = urlparse(line[1:])
                if parsed.hostname and is_valid_domain(parsed.hostname):
                    cleared_lines.append(parsed.hostname)
            except:
                continue
        
        # 处理纯域名格式
        elif is_valid_domain(line):
            cleared_lines.append(line)
    
    return cleared_lines


def is_valid_domain(domain):
    """验证域名格式"""
    if not domain:
        return False
    
    # 基本格式检查
    if len(domain) > 253:
        return False
    
    # 检查是否包含非法字符
    if not re.match(r'^[a-zA-Z0-9.-]+$', domain):
        return False
    
    # 检查是否以点开头或结尾
    if domain.startswith('.') or domain.endswith('.'):
        return False
    
    # 检查是否包含连续的点
    if '..' in domain:
        return False
    
    # 必须包含至少一个点
    if '.' not in domain:
        return False
    
    return True


def get_ad_rules():
    """获取广告过滤规则"""
    # 广告规则来源 URL
    ad_urls = [
        'https://easylist-downloads.adblockplus.org/easylistchina.txt',  # EasyList China
        'https://easylist-downloads.adblockplus.org/easylist.txt',       # EasyList
        'https://raw.githubusercontent.com/xinggsf/Adblock-Plus-Rule/master/rule.txt',  # 乘风规则
        'https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&showintro=0&mimetype=plaintext',  # Peter Lowe
    ]
    
    all_domains = set()
    
    for url in ad_urls:
        try:
            rule_text = get_rule(url)
            domains = clear_rule(rule_text)
            
            print(f'从 {url} 获取到 {len(domains)} 个域名')
            all_domains.update(domains)
            
        except Exception as e:
            print(f'获取规则失败 {url}: {e}')
            continue
    
    # 转换为列表并排序
    domain_list = list(all_domains)
    domain_list.sort()
    
    print(f'总共获取到 {len(domain_list)} 个唯一广告域名')
    return domain_list


def save_ad_rules(domains, output_file='resultant/ad.list'):
    """保存广告规则"""
    import os
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f'# 广告过滤规则\n')
        f.write(f'# 更新时间: {time.strftime("%Y-%m-%d %H:%M:%S")}\n')
        f.write(f'# 共计 {len(domains)} 个域名\n\n')
        
        for domain in domains:
            f.write(f'{domain}\n')
    
    print(f'广告规则已保存到: {output_file}')


if __name__ == '__main__':
    try:
        # 获取广告规则
        domains = get_ad_rules()
        
        if not domains:
            print('警告: 未获取到任何广告规则')
            sys.exit(1)
        
        # 保存到文件
        save_ad_rules(domains)
        
        print('广告规则获取完成')
        
    except Exception as e:
        print(f'错误: {e}')
        sys.exit(1)