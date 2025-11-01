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
    
    # 添加 [General] 配置段
    rules.append('[General]')
    rules.append('# 默认关闭 ipv6 支持，如果需要请手动开启')
    rules.append('ipv6 = false')
    rules.append('bypass-system = true')
    rules.append('skip-proxy = 192.168.0.0/16, 10.0.0.0/8, 172.16.0.0/12, fe80::/10, fc00::/7, localhost, *.local, *.lan, *.internal, e.crashlytics.com, captive.apple.com, sequoia.apple.com, seed-sequoia.siri.apple.com, *.ls.apple.com')
    rules.append('bypass-tun = 10.0.0.0/8,100.64.0.0/10,127.0.0.0/8,169.254.0.0/16,172.16.0.0/12,192.0.0.0/24,192.0.2.0/24,192.88.99.0/24,192.168.0.0/16,198.18.0.0/15,198.51.100.0/24,203.0.113.0/24,233.252.0.0/24,224.0.0.0/4,255.255.255.255/32,::1/128,::ffff:0:0/96,::ffff:0:0:0/96,64:ff9b::/96,64:ff9b:1::/48,100::/64,2001::/32,2001:20::/28,2001:db8::/32,2002::/16,3fff::/20,5f00::/16,fc00::/7,fe80::/10,ff00::/8')
    rules.append('dns-server = https://dns.alidns.com/dns-query, https://doh.pub/dns-query')
    rules.append('')
    
    # 添加 [Rule] 配置段
    rules.append('[Rule]')
    rules.append('#')
    rules.append('# GFWList + 广告过滤规则')
    rules.append('#')
    rules.append('')
    
    # 添加广告过滤规则（优先级最高）
    if ad_domains:
        rules.append('# 广告过滤规则')
        for domain in ad_domains:
            rules.append(f'DOMAIN-SUFFIX,{domain},REJECT')
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
    
    rules.append('')
    
    # 添加中国大陆 IP 段直连规则
    if cn_ip_ranges:
        rules.append('# 中国大陆 IP 段直连')
        for ip_range in cn_ip_ranges:
            rules.append(f'IP-CIDR,{ip_range},DIRECT')
        rules.append('')
    
    # 添加最终规则
    rules.append('# 最终规则')
    rules.append('GEOIP,CN,DIRECT')
    rules.append('FINAL,PROXY')
    rules.append('')
    
    # 添加 [URL Rewrite] 配置段（可选）
    rules.append('[URL Rewrite]')
    rules.append('^https?://(www.)?(g|google)\\.cn https://www.google.com 302')
    rules.append('')
    
    # 添加 [MITM] 配置段（可选）
    rules.append('[MITM]')
    rules.append('hostname = *.google.cn,*.googlevideo.com')
    rules.append('')
    
    # 添加尾部注释
    rules.append('# Generated from domain-list-community with ad blocking')
    
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