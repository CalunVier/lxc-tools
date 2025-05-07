#!/usr/bin/env python3
import argparse
import os
import sys

# cgroup 根路径
CGROUP_BASE = "/sys/fs/cgroup"

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
    # SI 使用 1000 为基数，否则使用 1024
    base = 1000 if si else 1024
    for unit in ['B', 'K', 'M', 'G', 'T', 'P']:
        if size_bytes < base or unit == 'P':
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= base

# 按指定单位转换
def format_unit(size_bytes, unit, si=False):
    unit = unit.upper()
    # SI 使用 1000, 否则 1024
    base = 1000 if si else 1024
    factor = {
        'B': 1,
        'K': base,
        'M': base**2,
        'G': base**3,
    }.get(unit, base)
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
                        help='show output in bytes')
    parser.add_argument('-k', '--kibi', action='store_const', const='K', dest='unit',
                        help='show output in KiB (default)')
    parser.add_argument('-m', '--mebi', action='store_const', const='M', dest='unit',
                        help='show output in MiB')
    parser.add_argument('-g', '--gibi', action='store_const', const='G', dest='unit',
                        help='show output in GiB')
    parser.add_argument('--si', action='store_true', dest='si',
                        help='use powers of 1000 not 1024')
    parser.add_argument('container', help='LXC container name or full cgroup path')
    args = parser.parse_args()

    # 确定 cgroup 路径
    c = args.container
    if os.path.isdir(c):
        cg_path = c
    else:
        candidates = [
            os.path.join(CGROUP_BASE, c),
            os.path.join(CGROUP_BASE, f"lxc.payload.{c}"),
            os.path.join(CGROUP_BASE, "lxc", c),
        ]
        for path in candidates:
            if os.path.isdir(path):
                cg_path = path
                break
        else:
            sys.stderr.write(f"Error: cgroup path for '{c}' not found.\n")
            sys.exit(1)

    # 读取 stats
    mem_cur = read_value(os.path.join(cg_path, 'memory.current'))
    mem_max = read_value(os.path.join(cg_path, 'memory.max'))
    swap_cur = read_value(os.path.join(cg_path, 'memory.swap.current'))
    swap_max = read_value(os.path.join(cg_path, 'memory.swap.max'))

    def calc(cur, mx):
        if cur is None:
            return 0, 0, 0
        total = mx if mx is not None else cur
        used = cur
        free = total - used
        return total, used, free

    m_total, m_used, m_free = calc(mem_cur, mem_max)
    s_total, s_used, s_free = calc(swap_cur, swap_max)

    # 选择格式化函数，根据--human和--si
    if args.human:
        fmt = lambda b: human_fmt(b, si=args.si)
    else:
        unit = args.unit or 'K'
        fmt = lambda b: f"{format_unit(b, unit, si=args.si):.0f}"

    # 准备表头和行数据
    headers = ["", "total", "used", "free"]
    rows = [
        ["Mem:", fmt(m_total), fmt(m_used), fmt(m_free)],
        ["Swap:", fmt(s_total), fmt(s_used), fmt(s_free)],
    ]

    # 按free逻辑，第一列宽度8，后面每列宽度12
    first_col_w = 8
    data_col_w = 12

    # 打印表头
    header_line = f"{'':{first_col_w}}" + ''.join(f"{h:>{data_col_w}}" for h in headers[1:])
    print(header_line)

    # 打印数据行
    for row in rows:
        label, *vals = row
        line = f"{label:<{first_col_w}}" + ''.join(f"{v:>{data_col_w}}" for v in vals)
        print(line)

if __name__ == '__main__':
    main()

