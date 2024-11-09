import json
import re
import sys

from io import SEEK_SET

# Mixture of things see on pp. 53 and in the encodings
ENC_ATOMS = re.compile("|".join([
    # literal bits
    "[01]+",
    # jmp offset
    "e-2",
    # bit operand
    "b",
    # integer literals
    "d",
    "n",
    # RST encoding specific
    "t",
    # two-byte register pairs
    "qq",
    "pp",
    "rr(?!')",
    "cc",
    "ss",
    # one-byte registers
    "A",
    "r'",
    r"r\*",
    "r",
    # catch-all (shouldn't get hit)
    "(?P<extra>.)"
]))

def gather_group(insts, f, page, inst):
    opcode = inst.split()[0]
    cur = []
    last = f.tell()
    while line := f.readline():
        line = line.strip()
        if not line:
            continue
        if line[0] == "#":
            f.seek(last, SEEK_SET)
            break
        last = f.tell()

        if line.startswith(opcode):
            if cur:
                insts.append(cur)
                cur = []
            zero = line.find("0")
            one = line.find("1")
            split = min(zero, one)
            if split == -1:
                split = max(zero, one)
                if split == -1:
                    raise Exception(f"On page {page} ({inst=}), {line=} did not cotain a 0 or 1")
            cur.append([page, line[:split]])
            cur.append(line[:split].removeprefix(opcode).strip())
            cur.append(line[split:])
        elif cur:
            cur.append(line)
    if cur:
        insts.append(cur)

def get_insts(filename):
    insts = []
    cur = []
    with open(filename) as f:
        while line := f.readline():
            line = line.strip()
            if not line:
                continue
            if line[0] == "#":
                if cur:
                    insts.append(cur)
                    cur = []
                page, inst = line.split(":")
                page = page.strip("# ")
                inst = inst.strip()
                # identify abbreviated pages (e.g., pp. 165 or pp. 170)
                # note ss represents a set of register pairs (see pp. 53)
                if inst.endswith("s") and not inst.endswith("ss") or inst.endswith("m"):
                    gather_group(insts, f, page, inst)
                else:
                    cur.append([page, inst])
            else:
                cur.append(line)
    if cur:
        insts.append(cur)
    return insts

def main(args):
    if len(args) != 2:
        print(f"Usage: {args[0]} <filename>", file=sys.stderr)
        return 1

    insts = []
    for inst in get_insts(args[1]):
        lines = iter(inst)
        page, inst = next(lines)
        page = int(re.search(r"\d+", page).group()) # type: ignore
        inst = inst.replace(", ", ",")
        if page == 277:
            # there's an image on this page, so we just hardcode the instruction
            insts.append({
                "page": page,
                "inst": inst,
                "op_code": inst.split()[0],
                "operands": ["cc", "nn"],
                "encoding": [["11","cc","010"], ["n"], ["n"]]
            })
            continue
        elif inst == "DEC (IY+d)":
            # everywhere else, the table appears in the Description section
            # So, instead of adjusting general parsing for this one case, we just hardcode it
            insts.append({
                "page": page,
                "inst": inst,
                "op_code": inst.split()[0],
                "operands": ["cc", "nn"],
                "encoding": [["11111101"], ["00110101"], ["d"]]
            })
            continue
        
        if page == 252 or page == 254:
            # These instructions take no operands, but on like elsewhere, the manual leaves these pages blank, instead
            # of using "None" 
            ops = []
        else:
            # sometimes the manual has lY instead of IY (presumably an OCR issue)
            # e.g., pp. 184
            ops = [op.strip().replace("lY", "IY") for op in next(lines).split(",")]
            if len(ops) == 1 and ops[0] in {"None", "None."}:
                ops = []
        encoding = []
        for line in lines:
            if len(line) > 8:
                if not line[:8].isnumeric():
                    print(page, "Skipping", line, file=sys.stderr)
                else:
                    # 8 bits + 2 hex digits
                    assert len(line) == 10
                    encoding.append([line[:8]])
            else:
                template = []
                for match in re.finditer(ENC_ATOMS, line):
                    if match.group("extra"):
                        print("Unexpected encoding symbol", page, inst, line, match.group(), file=sys.stderr, sep="\n")
                    else:
                        template.append(match.group())
                encoding.append(template)
        insts.append({
            "page": page,
            "inst": inst,
            "op_code": inst.split()[0],
            "operands": ops,
            "encoding": encoding
        })

    print(json.dumps(insts))

if __name__ == "__main__":
    exit(main(sys.argv))
