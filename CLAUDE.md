# CLAUDE.md

## Overview

pjhttptr is an HTTP "traceroute" tool that follows HTTP redirects, showing DNS resolution, IP addresses, protocol version, and response size at each hop. Written in Python using `httpx`.

## Running

```bash
./pjhttptr.py <url> [url ...]
./pjhttptr.py --http2 example.com
```

## Dependencies

- Python 3
- `httpx[http2]` (`pip install httpx[http2]`)

## Architecture

Single-file tool (`pjhttptr.py`):

- **`resolve_host(hostname)`** - Resolves hostname to IP and reverse DNS via `socket`
- **`trace_url(url, http_version)`** - Core loop: issues request, prints hop info, follows 3xx redirects manually
- **`main()`** - Argparse CLI with `--http1.1` / `--http2` flags (default HTTP/1.1)

Uses `httpx.Client` with `follow_redirects=False` so each redirect can be inspected individually.
