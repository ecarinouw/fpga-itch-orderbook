"""Decode a Nasdaq ITCH 5.0 file and print message counts and lengths by type.

Usage: python scripts/itch_stats.py path/to/sample.NASDAQ_ITCH50.gz
Each message in the file is a 2-byte big-endian length followed by the message,
whose first byte is the ASCII message type.
"""
import gzip
import struct
import sys
from collections import Counter


def main(path: str) -> None:
    counts: Counter[str] = Counter()
    lengths: dict[str, set[int]] = {}
    opener = gzip.open if path.endswith(".gz") else open

    with opener(path, "rb") as f:
        while True:
            hdr = f.read(2)
            if len(hdr) < 2:
                break
            (n,) = struct.unpack(">H", hdr)
            msg = f.read(n)
            if len(msg) < n:
                print(f"warning: truncated final message ({len(msg)} of {n} bytes)")
                break
            t = chr(msg[0])
            counts[t] += 1
            lengths.setdefault(t, set()).add(n)

    total = sum(counts.values())
    print(f"{total:,} messages")
    for t, c in counts.most_common():
        print(f"{t}  {c:>13,}  {100 * c / total:5.1f}%  len={sorted(lengths[t])}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
