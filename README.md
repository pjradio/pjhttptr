# pjhttptr - HTTP Traceroute

An HTTP "traceroute" tool that follows redirects, showing DNS resolution, IP addresses, protocol version, and response size at each hop.

Copyright (c) 2026, The Regents of the University of California. All rights reserved.

Author: Phil Jensen <pjensen3@ucmerced.edu>

## Features

- Follows HTTP redirects (301, 302, 303, 307, 308) showing each hop
- Resolves and displays IP address and reverse DNS for each host
- Shows response size in bytes and HTTP status code at each hop
- Supports HTTP/1.1 and HTTP/2 via `--http1.1` and `--http2` flags
- Accepts multiple URLs in a single invocation

## Requirements

- Python 3
- [httpx](https://www.python-httpx.org/) with HTTP/2 support

```bash
pip install httpx[http2]
```

## Usage

```bash
./pjhttptr.py <url> [url ...]
```

### Examples

```bash
# Trace a single URL (defaults to HTTP/1.1)
./pjhttptr.py example.com

# Force HTTP/2
./pjhttptr.py --http2 example.com

# Trace multiple URLs
./pjhttptr.py example.com github.com
```

### Sample Output

```
Tracing: https://example.com  (HTTP/1.1)

Hop   Status   Proto      Bytes  IP               DNS                                      URL
--------------------------------------------------------------------------------------------------------------------------------------------
0     200      HTTP/1.1     1256  93.184.216.34    example.com                              https://example.com
```

## License

All rights reserved. See source for details.
