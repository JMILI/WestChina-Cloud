#!/usr/bin/env python3
"""在 DNS 不可用时，通过固定 IP 映射安装 pip 包。"""
from __future__ import annotations

import socket
import sys

# PyPI / CDN（Fastly）
HOST_IP = {
    "pypi.org": "151.101.64.223",
    "files.pythonhosted.org": "151.101.64.223",
    "pypi.tuna.tsinghua.edu.cn": "101.201.38.215",
    "download.pytorch.org": "18.204.143.205",
}

_real_getaddrinfo = socket.getaddrinfo


def _patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    ip = HOST_IP.get(host)
    if ip:
        use_port = port or 443
        return [
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                socket.IPPROTO_TCP,
                "",
                (ip, use_port),
            )
        ]
    return _real_getaddrinfo(host, port, family, type, proto, flags)


def main() -> None:
    if len(sys.argv) < 2:
        print("用法: pip_dns_patch.py install -r requirements.txt", file=sys.stderr)
        raise SystemExit(2)

    socket.getaddrinfo = _patched_getaddrinfo
    sys.argv = ["pip"] + sys.argv[1:]
    from pip._internal.cli.main import main as pip_main

    raise SystemExit(pip_main())


if __name__ == "__main__":
    main()
