#!/usr/bin/env python3
"""Copy a Liberty file without the given cells (default: kit cells with 39 um height / metal2 0.93-0.95 um spacing)."""
import re, sys

DROP = ["XOR2X1", "XNOR2X1", "FAX1", "HAX1", "LATCH", "TBUFX1", "TBUFX2"]


def strip(text, names):
    out, pos = [], 0
    pat = re.compile(r"\n([ \t]*)cell\s*\((%s)\)\s*\{" % "|".join(names))
    while True:
        m = pat.search(text, pos)
        if not m:
            out.append(text[pos:])
            return "".join(out)
        out.append(text[pos:m.start()])
        depth, j = 0, m.end() - 1
        while True:
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        pos = j + 1


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    open(dst, "w").write(strip(open(src).read(), DROP))
