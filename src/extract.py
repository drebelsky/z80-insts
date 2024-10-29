import pymupdf
def get_page_numbers(doc):
    names = doc.resolve_names()
    pages = set()
    # z80 instrution set TOC
    for i in range(5, 10):
        page = doc[i]
        link = page.first_link
        while link:
            if not link.uri.startswith("#nameddest="):
                print(link.uri)
            else:
                pages.add(names[link.uri.split("=", 1)[1]]['page'])
            link = link.next

    # make sure we only grab the relevant parts
    return {page for page in pages if 84 <= page <= 328}

def get_span(text_dct, index):
    i, j, k = index
    return text_dct["blocks"][i]["lines"][j]["spans"][k]

def get_lines(dct, spans, start, end):
    """
    Get grouped lines of text using a text page dict between start and end.

    This is only intended to work for the instruction encoding lines we
    encounter in the Z80 user manual. Note that we have our own ordering code
    because of slight disrepancies with how lines are sorte using the sort
    method vs what we observe in the manual (e.g., the ADC A, n line on pdf
    page 165 or the different baselines between r' and r on pdf page 85).

    Args:
        dct (dict): the result of a pymupdf.TextPage.extractDICT call
        spans (list[tuple[int, int, int]]): an ordering of block, line, span indices
        start (int): the first index from spans to consider (inclusive)
        end (int): the first index from spans not to consider

    Returns:
        List of strings.
    """
    text = {}
    for i in range(start, end):
        span = get_span(dct, spans[i])
        y = span["origin"][1]
        # A little inefficient, but allows slight differeces between things in the same line
        for key, line in text.items():
            if abs(y - key) <= span["size"] / 2:
                break
        else:
            text[y] = line = []
        line.append((span["origin"][0], span["text"]))

    lines = []
    for key in sorted(text):
        line = text[key]
        lines.append("".join(word[1] for word in sorted(line)))

    return lines

def handle_page(page):
    dct = page.get_text("dict", sort=True) # type: ignore
    spans = []
    span_index = {}
    for i, block in enumerate(dct["blocks"]):
        # image block
        if block["type"] == 1:
            continue
        for j, line in enumerate(block["lines"]):
            for k, span in enumerate(line["spans"]):
                span_index[span["text"]] = len(spans)
                spans.append((i, j, k))

    inst = get_span(dct, spans[span_index["Operation"] - 1])["text"]

    print("\n# Page", page.number + 1, ":", inst.replace(" + ", "+"))

    start = span_index["Operands"] if "Operands" in span_index else span_index["Operand"]
    start += 1
    end = span_index["UM008011-0816"]
    for key in ["Description", "Z80 Instruction Description", "Z80 Instruction Set"]:
        if key in span_index:
            end = min(end, span_index[key])

    lines = get_lines(dct, spans, start, end)
    if len(lines) == 1 and lines[0] == "None.":
        print("None")
        start = span_index["Op Code"] + 2
        end = span_index["Operands"]
        lines = get_lines(dct, spans, start, end)
    # normalize
    print("\n".join(lines).replace("′", "'").replace("–", "-").replace(" + ", "+"))

def main():
    doc = pymupdf.open("um0080.pdf")
    inst_pages = get_page_numbers(doc)
    for page in sorted(inst_pages):
        handle_page(doc[page])


if __name__ == "__main__":
    main()
