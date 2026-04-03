#!/usr/bin/env python3
#
# Copyright (c) 2026, The Regents of the University of California.
# All rights reserved.
#
# Author: Phil Jensen <pjensen3@ucmerced.edu>
#
"""pjhttptr - HTTP traceroute: follow redirects showing DNS, IP, and bytes at each hop."""

import socket
import sys
from urllib.parse import urlparse

import requests


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


def trace_url(url):
    """Follow HTTP redirects, printing DNS/IP/bytes at each hop."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    hop = 0
    print(f"\nTracing: {url}\n")
    print(f"{'Hop':<5} {'Status':<8} {'Bytes':>10}  {'IP':<16} {'DNS':<40} {'URL'}")
    print("-" * 130)

    session = requests.Session()
    session.max_redirects = 30

    try:
        resp = session.get(url, allow_redirects=False, timeout=10)
    except requests.RequestException as e:
        print(f"Error connecting to {url}: {e}")
        return

    while True:
        parsed = urlparse(resp.url)
        hostname = parsed.hostname
        ip, rdns = resolve_host(hostname)
        ip_str = ip or "N/A"
        dns_str = rdns if rdns and rdns != hostname else hostname
        nbytes = len(resp.content)
        status = resp.status_code

        print(f"{hop:<5} {status:<8} {nbytes:>10}  {ip_str:<16} {dns_str:<40} {resp.url}")

        if resp.is_redirect or resp.is_permanent_redirect:
            location = resp.headers.get("Location")
            if not location:
                break
            # Handle relative redirects
            if location.startswith("/"):
                location = f"{parsed.scheme}://{parsed.netloc}{location}"
            hop += 1
            try:
                resp = session.get(location, allow_redirects=False, timeout=10)
            except requests.RequestException as e:
                print(f"\nError following redirect to {location}: {e}")
                return
        else:
            break

    print()


def print_banner():
    """Print the startup title banner."""
    print("=" * 70)
    print("  pjhttptr - HTTP Traceroute")
    print("  Copyright (c) 2026, The Regents of the University of California.")
    print("  All rights reserved.")
    print("  Author: Phil Jensen <pjensen3@ucmerced.edu>")
    print("=" * 70)


def main():
    print_banner()

    if len(sys.argv) < 2:
        print(f"\nUsage: {sys.argv[0]} <url> [url ...]")
        sys.exit(1)

    for url in sys.argv[1:]:
        trace_url(url)


if __name__ == "__main__":
    main()
