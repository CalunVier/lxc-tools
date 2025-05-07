#!/usr/bin/env python3
import argparse
import os
import sys

# cgroup 根路径
CGROUP_BASE = "/sys/fs/cgroup"

def get_sys_mem_info():
    """
    读取 /proc/meminfo 文件，返回系统总内存和总 swap，均以字节为单位。
    
    返回:
        tuple: (mem_total, swap_total)
               mem_total - 系统总内存 (bytes)
               swap_total - 系统总 swap (bytes)
    """
    mem_total = 0
    swap_total = 0

    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    # 格式示例: "MemTotal:       16305020 kB"
                    mem_total = int(line.split()[1]) * 1024  # 转换为字节
                elif line.startswith("SwapTotal:"):
                    swap_total = int(line.split()[1]) * 1024  # 转换为字节
                # 当两项都获取到就可以提前退出循环
                if mem_total and swap_total:
                    break
    except Exception as e:
        sys.stderr.write(f"Failed to read /proc/meminfo: {e}")
        exit(1)
    
    return mem_total, swap_total

SYSTEM_MEM_TOTAL, SYSTEM_SWAP_TOTAL = get_sys_mem_info()

# 读取文件中的整数值（"max" 视为无限）
def read_value(path):
    try:
        with open(path) as f:
            val = f.read().strip()
            if val == "max":
                return None
            return int(val)
    except Exception:
        return None

# 自动选择合适单位的输出
def format_auto(size_bytes, si=False):
    base = 1000 if si else 1024
    for unit in ['B', 'K', 'M', 'G', 'T', 'P']:
        if size_bytes < base or unit == 'P':
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= base

# 按指定单位转换
def format_unit(size_bytes, unit, si=False):
    base = 1000 if si else 1024
    unit = unit.upper()
    factor = {'B':1, 'K':base, 'M':base**2, 'G':base**3}.get(unit, base)
    return size_bytes / factor

# 人性化格式
def human_fmt(size_bytes, si=False):
    return format_auto(size_bytes, si)


def main():
    parser = argparse.ArgumentParser(
        description="Report LXC container memory usage (like `free`).",
        add_help=False
    )
    parser.add_argument('--help', action='help', help='show help and exit')
    parser.add_argument('-h', '--human', action='store_true', dest='human',
                        help='human-readable output (e.g. 512.0M)')
    parser.add_argument('-b', '--bytes', action='store_const', const='B', dest='unit',
                        help='show in bytes')
    parser.add_argument('-k', '--kibi', action='store_const', const='K', dest='unit',
                        help='show in KiB (default)')
    parser.add_argument('-m', '--mebi', action='store_const', const='M', dest='unit',
                        help='show in MiB')
    parser.add_argument('-g', '--gibi', action='store_const', const='G', dest='unit',
                        help='show in GiB')
    parser.add_argument('--si', action='store_true', dest='si',
                        help='use powers of 1000, not 1024')
    parser.add_argument('container', help='LXC container name or cgroup path')
    args = parser.parse_args()

    # 找到 cgroup 路径
    c = args.container
    cg = None
    if os.path.isdir(c):
        cg = c
    else:
        candidates = [
            os.path.join(CGROUP_BASE, c),
            os.path.join(CGROUP_BASE, f"lxc.payload.{c}"),
            os.path.join(CGROUP_BASE, "lxc", c),
            os.path.join(CGROUP_BASE, "memory", c),
            os.path.join(CGROUP_BASE, "memory", f"lxc.payload.{c}"),
            os.path.join(CGROUP_BASE, "memory", "lxc", c),
        ]
        for p in candidates:
            if os.path.isdir(p):
                cg = p
                break
        if cg is None:
            sys.stderr.write(f"Error: cgroup path for '{c}' not found.\n")
            sys.exit(1)

    # 读取 memory stats: 尝试 cgroup v2 文件 否则 cgroup v1 文件
    # v2
    mem_cur = read_value(os.path.join(cg, 'memory.current'))
    mem_max = read_value(os.path.join(cg, 'memory.max'))
    # v1 fallback
    if mem_cur is None and os.path.exists(os.path.join(cg, 'memory.usage_in_bytes')):
        mem_cur = read_value(os.path.join(cg, 'memory.usage_in_bytes'))
        mem_max = read_value(os.path.join(cg, 'memory.limit_in_bytes'))
        if mem_max > SYSTEM_MEM_TOTAL:
            mem_max = None
    # 读取 swap stats
    swap_cur = read_value(os.path.join(cg, 'memory.swap.current'))
    swap_max = read_value(os.path.join(cg, 'memory.swap.max'))
    if swap_cur is None and os.path.exists(os.path.join(cg, 'memory.memsw.usage_in_bytes')):
        swap_cur = read_value(os.path.join(cg, 'memory.memsw.usage_in_bytes')) - mem_cur
        # v1 swap limit is mem+swap; to get swap limit: limit_in_bytes - memory.limit
        total_memsw = read_value(os.path.join(cg, 'memory.memsw.limit_in_bytes'))
        swap_max = total_memsw - (mem_max or mem_cur)
        if swap_max > SYSTEM_SWAP_TOTAL:
            swap_max = None


    # 计算 total/used/free
    def calc(cur, mx):
        if cur is None:
            return 0, 0, 0
        total = mx if mx not in (None, 0) else cur
        used = cur
        free = total - used
        return total, used, free

    m_tot, m_use, m_free = calc(mem_cur, mem_max)
    s_tot, s_use, s_free = calc(swap_cur, swap_max)

    # 选择格式函数
    if args.human:
        fmt = lambda b: human_fmt(b, si=args.si)
    else:
        unit = args.unit or 'K'
        fmt = lambda b: f"{format_unit(b, unit, si=args.si):.0f}"

    # 输出表格
    headers = ["", "total", "used", "free"]
    rows = [
        ["Mem:", fmt(m_tot), fmt(m_use), fmt(m_free)],
        ["Swap:", fmt(s_tot), fmt(s_use), fmt(s_free)],
    ]
    # 固定宽度
    first_w = 8; col_w = 12
    print(f"{'':{first_w}}" + ''.join(f"{h:>{col_w}}" for h in headers[1:]))
    for row in rows:
        label, *vals = row
        print(f"{label:<{first_w}}" + ''.join(f"{v:>{col_w}}" for v in vals))

if __name__ == '__main__':
    main()
