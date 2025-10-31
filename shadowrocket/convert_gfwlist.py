#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将 domain-list-community 项目的数据转换为 Shadowrocket 规则
生成 GFWList 规则文件
"""

import os
import re
import time
import sys
from pathlib import Path


class DomainListParser:
    def __init__(self, data_path='../data'):
        self.data_path = Path(data_path)
        self.parsed_domains = set()
        self.parsed_includes = set()
        
    def parse_file(self, file_path):
        """解析单个域名列表文件"""
        domains = []
        includes = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # 跳过空行和注释
                    if not line or line.startswith('#'):
                        continue
                    
                    # 处理 include 指令
                    if line.startswith('include:'):
                        include_name = line[8:].strip()
                        includes.append(include_name)
                        continue
                    
                    # 处理域名条目
                    domain_entry = self.parse_domain_entry(line)
                    if domain_entry:
                        domains.append(domain_entry)
        
        except FileNotFoundError:
            print(f'警告: 文件不存在 {file_path}')
        except Exception as e:
            print(f'错误: 解析文件 {file_path} 失败: {e}')
        
        return domains, includes
    
    def parse_domain_entry(self, line):
        """解析域名条目"""
        # 移除属性标记 (@cn, @ads 等)
        if '@' in line:
            domain = line.split('@')[0].strip()
        else:
            domain = line.strip()
        
        # 处理不同的域名类型
        if line.startswith('full:'):
            return {'type': 'full', 'value': domain[5:]}
        elif line.startswith('keyword:'):
            return {'type': 'keyword', 'value': domain[8:]}
        elif line.startswith('regexp:'):
            return {'type': 'regexp', 'value': domain[7:]}
        elif self.is_valid_domain(domain):
            return {'type': 'domain', 'value': domain}
        
        return None
    
    def is_valid_domain(self, domain):
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
        
        return True
    
    def parse_list_recursive(self, list_name, visited=None):
        """递归解析列表，处理 include 指令"""
        if visited is None:
            visited = set()
        
        if list_name in visited:
            return []  # 避免循环引用
        
        visited.add(list_name)
        
        file_path = self.data_path / list_name
        if not file_path.exists():
            print(f'警告: 列表文件不存在 {file_path}')
            return []
        
        domains, includes = self.parse_file(file_path)
        all_domains = domains.copy()
        
        # 递归处理 include 的列表
        for include_name in includes:
            included_domains = self.parse_list_recursive(include_name, visited.copy())
            all_domains.extend(included_domains)
        
        return all_domains
    
    def get_gfw_domains(self):
        """获取 GFW 相关的域名列表"""
        # 主要的 GFW 相关列表
        gfw_lists = ['geolocation-!cn']
        
        all_domains = []
        for list_name in gfw_lists:
            domains = self.parse_list_recursive(list_name)
            all_domains.extend(domains)
        
        # 去重
        unique_domains = {}
        for domain in all_domains:
            key = f"{domain['type']}:{domain['value']}"
            unique_domains[key] = domain
        
        return list(unique_domains.values())


def convert_to_shadowrocket(domains, cn_ip_ranges=None, ad_domains=None):
    """转换为 Shadowrocket 规则格式"""
    rules = []
    
    # 添加头部注释
    rules.append('# Shadowrocket GFWList 规则')
    rules.append(f'# 生成时间: {time.strftime("%Y-%m-%d %H:%M:%S")}')
    rules.append(f'# 数据来源: domain-list-community')
    rules.append('')
    
    # 添加中国大陆 IP 段直连规则
    if cn_ip_ranges:
        rules.append('# 中国大陆 IP 段直连')
        for ip_range in cn_ip_ranges:
            rules.append(f'IP-CIDR,{ip_range},DIRECT')
        rules.append('')
    
    # 添加广告过滤规则
    if ad_domains:
        rules.append('# 广告过滤规则')
        for domain in ad_domains:
            rules.append(f'DOMAIN-SUFFIX,{domain},REJECT')
        rules.append('')
    
    # 添加 GFW 域名代理规则
    rules.append('# GFW 域名代理规则')
    for domain in domains:
        domain_type = domain['type']
        domain_value = domain['value']
        
        if domain_type == 'domain':
            rules.append(f'DOMAIN-SUFFIX,{domain_value},PROXY')
        elif domain_type == 'full':
            rules.append(f'DOMAIN,{domain_value},PROXY')
        elif domain_type == 'keyword':
            rules.append(f'DOMAIN-KEYWORD,{domain_value},PROXY')
        # regexp 类型在 Shadowrocket 中不直接支持，跳过
    
    # 添加最终规则
    rules.append('')
    rules.append('# 最终规则')
    rules.append('GEOIP,CN,DIRECT')
    rules.append('FINAL,PROXY')
    
    return rules


def load_cn_ip_ranges(file_path='resultant/cn_ip.list'):
    """加载中国大陆 IP 段"""
    ip_ranges = []
    
    if not os.path.exists(file_path):
        print(f'警告: 中国大陆 IP 段文件不存在 {file_path}')
        return ip_ranges
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    ip_ranges.append(line)
    except Exception as e:
        print(f'错误: 读取 IP 段文件失败: {e}')
    
    return ip_ranges


def load_ad_domains(file_path='resultant/ad.list'):
    """加载广告域名列表"""
    domains = []
    
    if not os.path.exists(file_path):
        print(f'警告: 广告域名文件不存在 {file_path}')
        return domains
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    domains.append(line)
    except Exception as e:
        print(f'错误: 读取广告域名文件失败: {e}')
    
    return domains


def save_shadowrocket_rules(rules, output_file):
    """保存 Shadowrocket 规则文件"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for rule in rules:
            f.write(rule + '\n')
    
    print(f'Shadowrocket 规则已保存到: {output_file}')


def main():
    """主函数"""
    try:
        # 初始化解析器
        parser = DomainListParser()
        
        # 获取 GFW 域名列表
        print('正在解析 GFW 域名列表...')
        gfw_domains = parser.get_gfw_domains()
        print(f'解析到 {len(gfw_domains)} 个 GFW 域名')
        
        # 加载中国大陆 IP 段
        print('正在加载中国大陆 IP 段...')
        cn_ip_ranges = load_cn_ip_ranges()
        print(f'加载了 {len(cn_ip_ranges)} 个 IP 段')
        
        # 生成 Shadowrocket_gfwlist 规则（仅 GFW）
        print('正在生成 Shadowrocket_gfwlist 规则...')
        gfwlist_rules = convert_to_shadowrocket(gfw_domains, cn_ip_ranges)
        save_shadowrocket_rules(gfwlist_rules, 'resultant/Shadowrocket_gfwlist.conf')
        
        print('GFWList 转换完成')
        
    except Exception as e:
        print(f'错误: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()