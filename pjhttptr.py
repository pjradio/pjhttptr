#!/usr/bin/env python3
#
# Copyright (c) 2026, The Regents of the University of California.
# All rights reserved.
#
# Author: Phil Jensen <pjensen3@ucmerced.edu>
#
"""pjhttptr - HTTP traceroute: follow redirects showing DNS, IP, and bytes at each hop."""

import argparse
import socket
import sys
import time
from urllib.parse import urlparse

import httpx


def resolve_host(hostname):
    """Resolve hostname to IP address and reverse DNS."""
    try:
        ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        return None, None
    try:
        rdns = socket.gethostbyaddr(ip)[0]
    except socket.herror:
        rdns = None
    return ip, rdns


def trace_url(url, http_version):
    """Follow HTTP redirects, printing DNS/IP/bytes at each hop."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    hop = 0
    proto_label = f"HTTP/{http_version}"
    print(f"\nTracing: {url}  ({proto_label})\n")
    print(f"{'Hop':<5} {'Time':>8}  {'Status':<8} {'Proto':<10} {'Bytes':>10}  {'IP':<16} {'DNS':<56} {'URL'}")
    print("-" * 170)

    use_http2 = (http_version == "2")
    client = httpx.Client(http2=use_http2, follow_redirects=False,
                          timeout=10.0, max_redirects=30)

    try:
        t0 = time.monotonic()
        resp = client.get(url)
        elapsed_ms = (time.monotonic() - t0) * 1000
    except httpx.HTTPError as e:
        print(f"Error connecting to {url}: {e}")
        client.close()
        return

    while True:
        parsed = urlparse(str(resp.url))
        hostname = parsed.hostname
        ip, rdns = resolve_host(hostname)
        ip_str = ip or "N/A"
        dns_str = rdns if rdns and rdns != hostname else hostname
        nbytes = len(resp.content)
        status = resp.status_code
        resp_proto = resp.http_version

        time_str = f"{elapsed_ms:.0f}ms"
        print(f"{hop:<5} {time_str:>8}  {status:<8} {resp_proto:<10} {nbytes:>10}  {ip_str:<16} {dns_str:<56} {str(resp.url)}")

        if status in (301, 302, 303, 307, 308):
            location = resp.headers.get("location")
            if not location:
                break
            # Handle relative redirects
            if location.startswith("/"):
                location = f"{parsed.scheme}://{parsed.netloc}{location}"
            hop += 1
            try:
                t0 = time.monotonic()
                resp = client.get(location)
                elapsed_ms = (time.monotonic() - t0) * 1000
            except httpx.HTTPError as e:
                print(f"\nError following redirect to {location}: {e}")
                client.close()
                return
        else:
            break

    client.close()
    print()


VERSION = "1.0.0"

VERSION_TEXT = (
    "pjhttptr " + VERSION + " - HTTP Traceroute\n"
    "Copyright (c) 2026, The Regents of the University of California.\n"
    "All rights reserved.\n"
    "Author: Phil Jensen <pjensen3@ucmerced.edu>"
)


def main():
    parser = argparse.ArgumentParser(
        description="HTTP traceroute: follow redirects showing DNS, IP, and bytes at each hop.",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--version", action="version", version=VERSION_TEXT)
    parser.add_argument("urls", nargs="+", metavar="URL", help="one or more URLs to trace")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--http1.1", dest="http_version", action="store_const",
                       const="1.1", help="force HTTP/1.1")
    group.add_argument("--http2", dest="http_version", action="store_const",
                       const="2", help="force HTTP/2")
    parser.set_defaults(http_version="1.1")

    args = parser.parse_args()

    for url in args.urls:
        trace_url(url, args.http_version)


if __name__ == "__main__":
    main()
