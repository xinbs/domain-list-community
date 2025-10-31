#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将 domain-list-community 项目的数据转换为 Shadowrocket 规则
生成 GFWList + 广告过滤规则文件
"""

import os
import sys
import time
from convert_gfwlist import DomainListParser, load_cn_ip_ranges, load_ad_domains, save_shadowrocket_rules


def convert_to_shadowrocket_with_ads(gfw_domains, cn_ip_ranges=None, ad_domains=None):
    """转换为 Shadowrocket 规则格式（包含广告过滤）"""
    rules = []
    
    # 添加头部注释
    rules.append('# Shadowrocket GFWList + 广告过滤规则')
    rules.append(f'# 生成时间: {time.strftime("%Y-%m-%d %H:%M:%S")}')
    rules.append(f'# 数据来源: domain-list-community + 多个广告过滤列表')
    rules.append('')
    
    # 添加广告过滤规则（优先级最高）
    if ad_domains:
        rules.append('# 广告过滤规则')
        for domain in ad_domains:
            rules.append(f'DOMAIN-SUFFIX,{domain},REJECT')
        rules.append('')
    
    # 添加中国大陆 IP 段直连规则
    if cn_ip_ranges:
        rules.append('# 中国大陆 IP 段直连')
        for ip_range in cn_ip_ranges:
            rules.append(f'IP-CIDR,{ip_range},DIRECT')
        rules.append('')
    
    # 添加 GFW 域名代理规则
    rules.append('# GFW 域名代理规则')
    for domain in gfw_domains:
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
        
        # 加载广告域名列表
        print('正在加载广告域名列表...')
        ad_domains = load_ad_domains()
        print(f'加载了 {len(ad_domains)} 个广告域名')
        
        # 生成 Shadowrocket_gfwlist_ad 规则（GFW + 广告过滤）
        print('正在生成 Shadowrocket_gfwlist_ad 规则...')
        gfwlist_ad_rules = convert_to_shadowrocket_with_ads(gfw_domains, cn_ip_ranges, ad_domains)
        save_shadowrocket_rules(gfwlist_ad_rules, 'resultant/Shadowrocket_gfwlist_ad.conf')
        
        print('GFWList + 广告过滤转换完成')
        
    except Exception as e:
        print(f'错误: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()