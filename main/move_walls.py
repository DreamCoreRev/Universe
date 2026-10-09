import re

PATH = "main.collection"

with open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Shift the 3 wall instances by the same screen-space delta that moved the
# room's back corner tile outward (grid (-1,-1) -> (-2,-2) = delta (0, +111)
# in this project's isometric math). This preserves each wall's exact
# rotation/scale (including the manual tuning Aurora did on wall_1 in the
# editor) and just relocates the whole 3-piece corner assembly to the new
# true back corner of the enlarged 5x5 room.
DX, DY = 0.0, 111.0
WALL_IDS = ["wall_1", "wall_2", "wall_3"]

# matches the *structural* top-level "position { x: .. y: .. [z: ..] }"
# block (real newlines + 4-space indent), not the escaped-string local
# collision-shape position that lives inside the data field as literal
# "position {\n" text.
pos_re = re.compile(
    r"\n  position \{\n    x: (-?[0-9.]+)\n    y: (-?[0-9.]+)\n"
)

for wall_id in WALL_IDS:
    marker = 'embedded_instances {\n  id: "%s"\n' % wall_id
    start = content.find(marker)
    assert start != -1, wall_id
    brace_start = content.find("{", start)
    depth = 1
    j = brace_start + 1
    while depth > 0:
        c = content[j]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        j += 1
    end = j
    block = content[start:end]

    def fmt(v):
        s = ("%.6f" % v).rstrip("0").rstrip(".")
        return s if "." in s else s + ".0"

    m = pos_re.search(block)
    assert m, "structural position not found in %s" % wall_id
    old_x = float(m.group(1))
    old_y = float(m.group(2))
    new_x = old_x + DX
    new_y = old_y + DY
    new_frag = "\n  position {\n    x: %s\n    y: %s\n" % (fmt(new_x), fmt(new_y))
    new_block = block[: m.start()] + new_frag + block[m.end():]
    print(wall_id, "old:", old_x, old_y, "-> new:", new_x, new_y)

    content = content[:start] + new_block + content[end:]

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("done, file length:", len(content))
