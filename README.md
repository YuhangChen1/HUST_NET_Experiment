# 🌐 计算机网络实验 Lab for 本硕博，智科，大数据

[![GitHub stars](https://img.shields.io/github/stars/yourusername/lab?style=social)](https://github.com/yourusername/lab)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/)
[![Mininet](https://img.shields.io/badge/mininet-2.3.0-green.svg)](http://mininet.org/)

> 📚 **完整的计算机网络实验集合**，涵盖网络拓扑构建、SDN 控制器、流表配置等核心内容

## ⭐ 如果这个项目对你有帮助，请给个 Star！

---

## 📂 实验内容

### Lab 1: FAT TREE 拓扑实验 ✅


👉 **[查看 Lab 1 详细指南](lab1/README.md)**

---

### Lab 2: [敬请期待...] 🚧

敬请期待...

👉 **[查看 Lab 2 详细指南](lab2/README.md)**

敬请期待...

### Lab 3: [敬请期待...]🚧

敬请期待...

👉 **[查看 Lab 3 详细指南](lab3/README.md)**

敬请期待...

## 🚀 快速开始

### 环境要求

```bash
# 操作系统
Ubuntu 18.04 / 20.04 / 22.04 (推荐使用虚拟机)

# 必需软件
- Python 3.6+
- Mininet 2.3.0+
- Open vSwitch 2.9.0+
```

### 安装 Mininet

```bash
# 方法 1：使用官方脚本（推荐）
git clone https://github.com/mininet/mininet
cd mininet
git checkout 2.3.0
./util/install.sh -a

# 方法 2：使用 apt（Ubuntu）
sudo apt update
sudo apt install mininet openvswitch-switch
```

### 克隆本仓库

```bash
git clone https://github.com/yourusername/lab.git
cd lab
```

### 运行第一个实验

```bash
cd lab1
sudo python3 fat_tree_topo.py
```

🎉 **30 秒后看到 pingall 成功！**

---

## 📖 使用指南

每个实验文件夹都包含：

```
lab1/
├── README.md              # 📘 详细的实验指南
├── fat_tree_topo.py       # ✅ 完整工作版本
├── fat_tree_topo_4_bad.py # ❌ 问题演示版本
├── debug.py               # 🔧 调试版本
└── [其他辅助文件]
```

**请务必先阅读各个实验的 README.md 文件！**

里面包含：
- ✅ 详细的实验步骤
- 📊 数据收集方法
- 🐛 常见问题及解决方案
- 📸 实验报告模板
- 🎯 演示技巧

---

<!-- ## 🎯 实验特色

### 1. 多版本脚本设计

每个实验提供 **3 个版本**：

| 版本 | 用途 | 适合场景 |
|------|------|----------|
| 完整版 | 自动配置，一键成功 | 快速验证，最终演示 |
| 问题版 | 展示常见错误 | 学习排查过程，理解原理 |
| 调试版 | 手动配置测试 | 深入学习，自主探索 | -->

<!-- ### 2. 完整的问题诊断流程

不只是"能跑的代码"，更重要的是：
- 🔍 **为什么会失败？** - 深入分析根本原因
- 🛠️ **如何诊断？** - 提供完整的调试命令
- ✅ **如何解决？** - 逐步解决每个问题
- 📚 **背后原理？** - 解释技术细节 -->

<!-- ### 3. 实验报告模板

每个实验都提供：
- 📝 完整的报告结构
- 📊 数据收集方法
- 📸 截图建议
- 💡 分析思路 -->

---

## 🤝 贡献指南

欢迎贡献！可以通过以下方式参与：

1. 🐛 **报告 Bug**：发现问题请提 Issue
2. 💡 **提出建议**：改进想法请提 Issue
3. 🔧 **提交代码**：欢迎 Pull Request
4. 📖 **完善文档**：改进 README 或注释
5. ⭐ **给个 Star**：这是对我们最大的鼓励！

### 提交 Pull Request

```bash
# 1. Fork 本仓库
# 2. 创建你的分支
git checkout -b feature/amazing-feature

# 3. 提交改动
git commit -m "Add some amazing feature"

# 4. 推送到分支
git push origin feature/amazing-feature

# 5. 提交 Pull Request
```

---

## 📚 学习资源

### 推荐阅读

- 📖 [Mininet 官方文档](http://mininet.org/)
- 📖 [Open vSwitch 文档](https://www.openvswitch.org/)
- 📄 [FAT TREE 原始论文](https://cseweb.ucsd.edu/~vahdat/papers/sigcomm08.pdf)
- 📘 [SDN 权威指南](https://github.com/SDN-Guide)

### 视频教程

- 🎥 [Mininet 入门教程](https://www.youtube.com/results?search_query=mininet+tutorial)
- 🎥 [SDN 基础课程](https://www.youtube.com/results?search_query=sdn+tutorial)

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

```
MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files...
```

---

## 💬 联系方式

有问题或建议？

计算机学院都知道我是谁吧（

---

## 🌟 Star History

如果这个项目帮助到了你，请点击右上角的 ⭐ **Star** 按钮！

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/lab&type=Date)](https://star-history.com/#yourusername/lab&Date)

<!-- --- -->

<!-- ## 📊 项目统计

![GitHub last commit](https://img.shields.io/github/last-commit/yourusername/lab)
![GitHub issues](https://img.shields.io/github/issues/yourusername/lab)
![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/lab)
![GitHub contributors](https://img.shields.io/github/contributors/yourusername/lab)

--- -->

<div align="center">

### ⭐ 如果觉得有用，别忘了给个 Star！⭐

**[⬆ 回到顶部](#-计算机网络实验-lab)**

Made with ❤️ by Network Lab Team

</div>

