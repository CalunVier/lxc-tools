# lxc-proxy
[English](README.md) | [简体中文](README_cn.md)

通过 lxc-attach 的标准输入输出创建端口映射。代码通过 AI 生成，我本人并不会写 Bash。但是程序经过简单测试，基本可用。欢迎 Bash 专家优化代码。

目前只支持 TCP 连接（UDP代码我还没有审查完）

## 依赖
- socat
- getopt

## 使用方式
```
Usage: lxc-proxy -n NAME [-l [ADDR:]PORT] [-d [ADDR:]PORT]
  -n, --name         LXC 容器名称（必填）
  -l, --listen       本地监听地址和端口，格式 addr:port 或 port（默认 0.0.0.0:PORT）
  -d, --destination  容器内目标地址和端口，格式 addr:port 或 port（默认 127.0.0.1:PORT）
  -h, --help         显示此帮助
```