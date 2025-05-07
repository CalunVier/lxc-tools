# lxc-tools
[English](README.md) | [简体中文](README_cn.md)

本仓库包含我编写的一些 lxc 工具（脚本），以补充基础 lxc-* 系列命令功能孱弱的问题。

目前包含以下脚本

- lxc-proxy 通过 lxc-attach 的标准输入输出创建端口映射。以在完全隔离网络环境的情况下转发流量。目前只支持 TCP 连接。
- lxc-free 获取 lxc 容器占用的内存情况

## lxc-proxy
### 依赖
- socat (容器和主机都需要安装)
- getopt

### 使用方式
```
Usage: lxc-proxy -n NAME [-l [ADDR:]PORT] [-d [ADDR:]PORT]
  -n, --name         LXC 容器名称（必填）
  -l, --listen       本地监听地址和端口，格式 addr:port 或 port（默认 0.0.0.0:PORT）
  -d, --destination  容器内目标地址和端口，格式 addr:port 或 port（默认 127.0.0.1:PORT）
  -h, --help         显示此帮助
```

例如，将容器中的22端口映射到主机的2222上

```
# lxc-proxy -n container_name -l 2222 -d 22
Starting port forwarding: Host [0.0.0.0:2222] → Container container_name [127.0.0.1:22]
```


## lxc-free

### 依赖

`lxc-free` 脚本为 `bash` 实现，`lxc-free.py` 为 `python3` 实现。两者功能完全相同。

- lxc-free
  - awk
  - getopt
- lxc-free.py
  - python3

### 使用方式
```
用法: lxc-free [--help] [-h] [-b] [-k] [-m] [-g] [--si] container

报告 LXC 容器的内存使用情况（类似于 'free'）。

位置参数:
  container    LXC 容器名称或完整的 cgroup 路径

可选参数:
  --help       显示帮助并退出
  -h, --human  以可读格式显示输出（例如 512.0M）
  -b, --bytes  以字节为单位显示输出
  -k, --kibi   以 KiB 显示输出（默认）
  -m, --mebi   以 MiB 显示输出
  -g, --gibi   以 GiB 显示输出
  --si         使用 1000 的幂而非 1024
```

例如

```
# sudo ./lxc-free -h container-name
               total        used        free
Mem:            9.4G        9.4G        0.0B
Swap:         938.2M      938.2M        0.0B
```
