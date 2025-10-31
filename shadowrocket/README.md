# Shadowrocket 规则生成器

基于 domain-list-community 项目数据，自动生成 Shadowrocket 代理规则文件。

## 功能特性

- 🌐 **GFWList 规则**: 基于 domain-list-community 的 `geolocation-!cn` 数据生成代理规则
- 🚫 **广告过滤**: 集成多个广告过滤列表，自动屏蔽广告域名
- 🇨🇳 **中国大陆直连**: 自动获取最新的中国大陆 IP 段，实现直连访问
- 📱 **Shadowrocket 兼容**: 生成的规则完全兼容 Shadowrocket 应用

## 生成的规则文件

1. **Shadowrocket_gfwlist.conf** - 纯 GFWList 规则
   - GFW 屏蔽的域名走代理
   - 中国大陆 IP 段直连
   - 其他流量根据 GeoIP 判断

2. **Shadowrocket_gfwlist_ad.conf** - GFWList + 广告过滤规则
   - 包含上述 GFWList 功能
   - 额外屏蔽广告域名
   - 推荐日常使用

## 数据来源

### GFWList 数据
- **来源**: [domain-list-community](https://github.com/v2fly/domain-list-community) 项目
- **列表**: `geolocation-!cn` (被 GFW 屏蔽的域名)
- **更新**: 跟随上游项目更新

### 广告过滤数据
- **EasyList China**: 中文广告过滤规则
- **EasyList**: 国际广告过滤规则  
- **乘风规则**: 中文广告过滤补充
- **Peter Lowe**: 广告服务器列表

### 中国大陆 IP 段
- **来源**: https://ispip.clang.cn/all_cn.html
- **格式**: CIDR 格式的 IPv4 地址段
- **用途**: 实现中国大陆 IP 直连

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 快速开始

运行主构建脚本，一键生成所有规则：

```bash
cd shadowrocket
python build_shadowrocket_rules.py
```

### 单独运行

也可以单独运行各个脚本：

```bash
# 获取中国大陆 IP 段
python fetch_cn_ip.py

# 获取广告过滤规则
python fetch_ad_rules.py

# 生成 GFWList 规则
python convert_gfwlist.py

# 生成 GFWList + 广告过滤规则
python convert_gfwlist_ad.py
```

## 导入 Shadowrocket

1. 将生成的 `.conf` 文件传输到 iOS 设备
2. 在 Shadowrocket 中点击右上角 `+` 号
3. 选择 `从文件导入` 或 `从 URL 导入`
4. 选择对应的配置文件
5. 启用配置并开始使用

## 文件结构

```
shadowrocket/
├── build_shadowrocket_rules.py    # 主构建脚本
├── fetch_cn_ip.py                 # 获取中国大陆 IP 段
├── fetch_ad_rules.py              # 获取广告过滤规则
├── convert_gfwlist.py             # 转换 GFWList 规则
├── convert_gfwlist_ad.py          # 转换 GFWList + 广告规则
├── requirements.txt               # Python 依赖
├── README.md                      # 说明文档
└── resultant/                     # 输出目录
    ├── cn_ip.list                 # 中国大陆 IP 段
    ├── ad.list                    # 广告域名列表
    ├── Shadowrocket_gfwlist.conf  # GFWList 规则
    └── Shadowrocket_gfwlist_ad.conf # GFWList + 广告规则
```

## 规则说明

### 规则优先级

1. **广告过滤** (REJECT) - 最高优先级
2. **中国大陆 IP** (DIRECT) - 直连访问
3. **GFW 域名** (PROXY) - 代理访问
4. **GeoIP 中国** (DIRECT) - 地理位置判断
5. **其他流量** (PROXY) - 默认代理

### 规则类型

- `DOMAIN-SUFFIX`: 域名后缀匹配
- `DOMAIN`: 完整域名匹配
- `DOMAIN-KEYWORD`: 域名关键词匹配
- `IP-CIDR`: IP 地址段匹配
- `GEOIP`: 地理位置匹配

## 注意事项

1. **网络要求**: 脚本需要访问外部网站获取数据，请确保网络连接正常
2. **更新频率**: 建议定期运行脚本更新规则，保持数据最新
3. **文件大小**: 生成的规则文件可能较大，请注意设备存储空间
4. **兼容性**: 规则专为 Shadowrocket 设计，其他客户端可能需要调整

## 故障排除

### 常见问题

**Q: 脚本运行失败，提示网络错误**
A: 检查网络连接，确保可以访问外部网站。如果在中国大陆，可能需要先配置代理。

**Q: 生成的规则文件过大**
A: 这是正常现象，完整的规则集包含大量域名。可以考虑只使用 GFWList 规则。

**Q: 某些网站无法访问**
A: 检查域名是否在规则中，可能需要手动添加到代理列表。

## 许可证

本项目基于 MIT 许可证开源，详见 LICENSE 文件。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进项目。

## 相关项目

- [domain-list-community](https://github.com/v2fly/domain-list-community) - 域名列表社区维护项目
- [Shadowrocket-ADBlock-Rules-Forever](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever) - 参考的规则生成项目