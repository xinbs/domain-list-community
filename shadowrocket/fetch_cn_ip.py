#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
获取中国大陆 IP 段数据
优先使用 clang.cn，并在源站不可用时自动切换备用数据源。
"""

import ipaddress
import re
import sys
import time

import requests


SOURCES = (
    # Prefer the plain-text endpoint. It contains the same data as the HTML page
    # but is less likely to break when the page layout changes.
    'https://ispip.clang.cn/all_cn_cidr.txt',
    'https://ispip.clang.cn/all_cn.html',
    # Independent mirrors keep the scheduled build working when clang.cn is
    # temporarily unavailable from a GitHub Actions runner.
    'https://www.ipdeny.com/ipblocks/data/aggregated/cn-aggregated.zone',
    'https://raw.githubusercontent.com/17mon/china_ip_list/master/china_ip_list.txt',
)

MIN_EXPECTED_RANGES = 1000
REQUEST_TIMEOUT = 30
RETRIES_PER_SOURCE = 2


def get_cn_ip_ranges():
    """获取中国大陆 IP 段列表"""
    errors = []

    for url in SOURCES:
        print(f'正在获取中国大陆 IP 段数据: {url}', flush=True)
        for attempt in range(1, RETRIES_PER_SOURCE + 1):
            try:
                response = requests.get(
                    url,
                    headers={'User-Agent': 'domain-list-community-shadowrocket-builder/1.0'},
                    timeout=REQUEST_TIMEOUT,
                )
                response.raise_for_status()
                ip_ranges = parse_cn_ip_ranges(response.text)
                if len(ip_ranges) < MIN_EXPECTED_RANGES:
                    raise ValueError(
                        f'仅解析到 {len(ip_ranges)} 个 IP 段，低于安全阈值 '
                        f'{MIN_EXPECTED_RANGES}'
                    )

                print(f'成功从 {url} 获取 {len(ip_ranges)} 个中国大陆 IP 段')
                return ip_ranges, url
            except (requests.RequestException, ValueError) as exc:
                message = f'{url} 第 {attempt}/{RETRIES_PER_SOURCE} 次尝试失败: {exc}'
                print(f'警告: {message}', file=sys.stderr, flush=True)
                errors.append(message)
                if attempt < RETRIES_PER_SOURCE:
                    time.sleep(2)

    raise RuntimeError('所有中国大陆 IP 数据源均不可用:\n- ' + '\n- '.join(errors))


def parse_cn_ip_ranges(content):
    """从纯文本或 HTML 内容中提取、验证并按网络地址排序 IPv4 CIDR。"""
    cidr_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}/[0-9]{1,2}\b'
    networks = set()
    for match in re.findall(cidr_pattern, content):
        try:
            network = ipaddress.ip_network(match, strict=True)
        except ValueError:
            continue
        if network.version == 4:
            networks.add(network)

    return [str(network) for network in sorted(networks)]


def validate_cidr(cidr):
    """验证 CIDR 格式的 IP 段"""
    try:
        return ipaddress.ip_network(cidr, strict=True).version == 4
    except ValueError:
        return False


def save_cn_ip_list(ip_ranges, source_url, output_file='resultant/cn_ip.list'):
    """保存中国大陆 IP 段列表"""
    import os
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f'# 中国大陆 IP 段列表\n')
        f.write(f'# 数据来源: {source_url}\n')
        f.write(f'# 更新时间: {time.strftime("%Y-%m-%d %H:%M:%S")}\n')
        f.write(f'# 共计 {len(ip_ranges)} 个 IP 段\n\n')
        
        for ip_range in ip_ranges:
            f.write(f'{ip_range}\n')
    
    print(f'中国大陆 IP 段列表已保存到: {output_file}')


if __name__ == '__main__':
    try:
        # 获取中国大陆 IP 段
        ip_ranges, source_url = get_cn_ip_ranges()
        
        if not ip_ranges:
            print('警告: 未获取到任何 IP 段数据')
            sys.exit(1)
        
        # 保存到文件
        save_cn_ip_list(ip_ranges, source_url)
        
        print('中国大陆 IP 段数据获取完成')
        
    except Exception as e:
        print(f'错误: {e}')
        sys.exit(1)
