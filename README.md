# lxc-tools

[English](README.md) | [简体中文](README_cn.md)

This repository contains some LXC tools (scripts) I wrote to supplement the limited functionality of the basic `lxc-*` command series.

Currently, it includes the following scripts:

* **lxc-proxy**: Creates port forwarding using the standard input/output of `lxc-attach`, allowing traffic forwarding in a fully isolated network environment. Currently supports only TCP connections.
* **lxc-free**: Retrieves memory usage information of an LXC container.

## lxc-proxy

### Dependencies

* `socat` (must be installed both in the container and on the host)
* `getopt`

### Usage

```
Usage: lxc-proxy -n NAME [-l [ADDR:]PORT] [-d [ADDR:]PORT]
  -n, --name         LXC container name (required)
  -l, --listen       Local listen address and port, format addr:port or port (default 0.0.0.0:PORT)
  -d, --destination  Destination address and port inside container, format addr:port or port (default 127.0.0.1:PORT)
  -h, --help         Show this help message
```

For example, to map port 22 inside the container to port 2222 on the host:

```
# lxc-proxy -n container_name -l 2222 -d 22
Starting port forwarding: Host [0.0.0.0:2222] → Container container_name [127.0.0.1:22]
```

## lxc-free

### Dependencies

The `lxc-free` script is implemented in `bash`, while `lxc-free.py` is implemented in `python3`. Both have identical functionality.

* **lxc-free**

  * `awk`
  * `getopt`
* **lxc-free.py**

  * `python3`

### Usage

```
usage: lxc-free [--help] [-h] [-b] [-k] [-m] [-g] [--si] container

Report LXC container memory usage (like 'free').

positional arguments:
  container    LXC container name or full cgroup path

optional arguments:
  --help       show help and exit
  -h, --human  human-readable output (e.g. 512.0M)
  -b, --bytes  show output in bytes
  -k, --kibi   show output in KiB (default)
  -m, --mebi   show output in MiB
  -g, --gibi   show output in GiB
  --si         use powers of 1000 not 1024
```

For example:

```
# sudo ./lxc-free -h container-name
               total        used        free
Mem:            9.4G        9.4G        0.0B
Swap:         938.2M      938.2M        0.0B
```
