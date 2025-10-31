#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取中国大陆 IP 段数据并生成 Shadowrocket 绕过配置
数据源: https://ispip.clang.cn/all_cn.html
"""

import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path
from datetime import datetime
import sys

def fetch_cn_ip_ranges():
    """
    从 https://ispip.clang.cn/all_cn.html 获取中国大陆 IP 段
    """
    url = "https://ispip.clang.cn/all_cn.html"
    
    try:
        print(f"🌐 正在从 {url} 获取中国大陆 IP 段...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找包含 IP 段的内容
        ip_ranges = []
        
        # 尝试多种方式提取 IP 段
        # 方式1: 查找所有文本中的 CIDR 格式
        text_content = soup.get_text()
        cidr_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}/[0-9]{1,2}\b'
        found_cidrs = re.findall(cidr_pattern, text_content)
        
        if found_cidrs:
            ip_ranges.extend(found_cidrs)
            print(f"✅ 通过正则表达式找到 {len(found_cidrs)} 个 IP 段")
        
        # 方式2: 查找 pre 标签或 code 标签
        for tag in soup.find_all(['pre', 'code', 'textarea']):
            tag_text = tag.get_text()
            tag_cidrs = re.findall(cidr_pattern, tag_text)
            if tag_cidrs:
                ip_ranges.extend(tag_cidrs)
                print(f"✅ 从 {tag.name} 标签找到 {len(tag_cidrs)} 个 IP 段")
        
        # 去重并排序
        ip_ranges = sorted(list(set(ip_ranges)))
        
        if not ip_ranges:
            print("⚠️  未找到 IP 段，尝试获取原始文本...")
            # 如果没有找到，可能需要其他解析方式
            print("页面内容预览:")
            print(text_content[:500] + "..." if len(text_content) > 500 else text_content)
            
            # 尝试查找可能的 IP 段格式
            ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
            ips = re.findall(ip_pattern, text_content)
            if ips:
                print(f"找到 {len(ips)} 个 IP 地址，但没有 CIDR 格式")
        
        print(f"📊 总共获取到 {len(ip_ranges)} 个中国大陆 IP 段")
        return ip_ranges
        
    except requests.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        return []
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        return []

def generate_shadowrocket_bypass_config(ip_ranges, output_file='resultant/Shadowrocket_bypass_cn_ip.config'):
    """
    生成 Shadowrocket 绕过中国大陆 IP 的配置文件
    """
    if not ip_ranges:
        print("❌ 没有 IP 段数据，无法生成配置文件")
        return False
    
    # 确保输出目录存在
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 生成配置内容
    config_lines = []
    
    # 添加配置文件头部
    config_lines.append("# Shadowrocket 绕过中国大陆 IP 配置")
    config_lines.append(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    config_lines.append(f"# 数据源: https://ispip.clang.cn/all_cn.html")
    config_lines.append(f"# IP 段数量: {len(ip_ranges)}")
    config_lines.append("#")
    config_lines.append("# 使用说明:")
    config_lines.append("# 1. 中国大陆 IP 直连 (DIRECT)")
    config_lines.append("# 2. 其他 IP 走代理 (PROXY)")
    config_lines.append("#")
    config_lines.append("")
    
    # 添加通用配置
    config_lines.append("[General]")
    config_lines.append("bypass-system = true")
    config_lines.append("skip-proxy = 192.168.0.0/16, 10.0.0.0/8, 172.16.0.0/12, localhost, *.local, captive.apple.com")
    config_lines.append("bypass-tun = 10.0.0.0/8, 100.64.0.0/10, 127.0.0.0/8, 169.254.0.0/16, 172.16.0.0/12, 192.0.0.0/24, 192.0.2.0/24, 192.88.99.0/24, 192.168.0.0/16, 198.18.0.0/15, 198.51.100.0/24, 203.0.113.0/24, 224.0.0.0/4, 255.255.255.255/32")
    config_lines.append("dns-server = system")
    config_lines.append("")
    
    # 添加规则部分
    config_lines.append("[Rule]")
    
    # 添加中国大陆 IP 段规则 (直连)
    for ip_range in ip_ranges:
        config_lines.append(f"IP-CIDR,{ip_range},DIRECT")
    
    # 添加最终规则
    config_lines.append("")
    config_lines.append("# 最终规则")
    config_lines.append("FINAL,PROXY")
    
    # 写入文件
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(config_lines))
        
        print(f"✅ 配置文件已生成: {output_path}")
        print(f"📊 包含 {len(ip_ranges)} 个中国大陆 IP 段规则")
        
        # 显示文件信息
        file_size = output_path.stat().st_size
        line_count = len(config_lines)
        print(f"📄 文件大小: {file_size:,} 字节")
        print(f"📝 总行数: {line_count:,} 行")
        
        return True
        
    except Exception as e:
        print(f"❌ 写入文件失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始生成 Shadowrocket 绕过中国大陆 IP 配置...")
    print("=" * 50)
    
    # 获取中国大陆 IP 段
    ip_ranges = fetch_cn_ip_ranges()
    
    if not ip_ranges:
        print("❌ 未能获取到 IP 段数据")
        sys.exit(1)
    
    # 生成配置文件
    success = generate_shadowrocket_bypass_config(ip_ranges)
    
    if success:
        print("\n🎉 配置文件生成完成!")
        print("\n📋 使用说明:")
        print("1. 将生成的 .config 文件导入到 Shadowrocket")
        print("2. 中国大陆 IP 将直接连接，其他 IP 走代理")
        print("3. 适用于需要绕过中国大陆 IP 的场景")
    else:
        print("❌ 配置文件生成失败")
        sys.exit(1)

if __name__ == "__main__":
    main()