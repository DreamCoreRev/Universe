import sys

PATH = "main.collection"

with open(PATH, "r", encoding="utf-8") as f:
    original = f.read()


def extract_instance_block(text, instance_id):
    marker = 'embedded_instances {\n  id: "%s"\n' % instance_id
    start = text.find(marker)
    if start == -1:
        raise RuntimeError("marker not found: %s" % instance_id)
    brace_start = text.find("{", start)
    depth = 1
    j = brace_start + 1
    while depth > 0:
        c = text[j]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        j += 1
    end = j
    return text[start:end], start, end


# --- templates, extracted verbatim from the live file (no hand-typed escaping) ---
no_boundary_tpl, _, _ = extract_instance_block(original, "floor_n1n1")
with_boundary_tpl, _, _ = extract_instance_block(original, "floor_11")

assert "boundary" not in no_boundary_tpl
assert "boundary" in with_boundary_tpl
print("template lengths:", len(no_boundary_tpl), len(with_boundary_tpl))

# --- step 1: the 5 tiles that become interior lose their boundary collider ---
# the boundary sub-block text is byte-identical on all 5 tiles and appears
# nowhere else in the file, so extracting it once and stripping every
# occurrence is safe and exact (no hand-typed escaped text involved).
b_marker = '"embedded_components {\\n"\n  "  id: \\"boundary\\"\\n"'
b_start = with_boundary_tpl.find(b_marker)
assert b_start != -1
b_end_marker = '  ""\n  position {'
b_end = with_boundary_tpl.find(b_end_marker, b_start)
assert b_end != -1
boundary_chunk = with_boundary_tpl[b_start:b_end]
print("boundary chunk length:", len(boundary_chunk))

occurrences = original.count(boundary_chunk)
print("boundary chunk occurrences in file:", occurrences)
assert occurrences == 5, occurrences

content = original.replace(boundary_chunk, "")

# --- step 2: build the 16 new floor tiles for the 5x5 grid ---
# screen_x = 480 + (gx - gy) * 75.5 ; screen_y = 300 - (gx + gy) * 55.5
HALF_W = 75.5
HALF_H = 55.5
CX, CY = 480.0, 300.0


def gid(gx, gy):
    def part(v):
        return ("n%d" % -v) if v < 0 else ("%d" % v)
    return "floor_%s%s" % (part(gx), part(gy))


def pos(gx, gy):
    x = CX + (gx - gy) * HALF_W
    y = CY - (gx + gy) * HALF_H
    return x, y


new_coords = []
for gx in range(-2, 3):
    for gy in range(-2, 3):
        if -1 <= gx <= 1 and -1 <= gy <= 1:
            continue  # already exists
        new_coords.append((gx, gy))

assert len(new_coords) == 16, len(new_coords)

# the 3 tiles immediately beyond the old back corner stay wall-enclosed
# (same relative shape as the original corner, just shifted outward)
WALLED = {(-2, -2), (-2, -1), (-1, -2)}

new_blocks = []
for gx, gy in new_coords:
    new_id = gid(gx, gy)
    x, y = pos(gx, gy)
    if (gx, gy) in WALLED:
        block = no_boundary_tpl.replace('id: "floor_n1n1"', 'id: "%s"' % new_id, 1)
        block = block.replace("x: 480.0\n    y: 411.0", "x: %.1f\n    y: %.1f" % (x, y), 1)
    else:
        block = with_boundary_tpl.replace('id: "floor_11"', 'id: "%s"' % new_id, 1)
        block = block.replace("x: 480.0\n    y: 189.0", "x: %.1f\n    y: %.1f" % (x, y), 1)
    new_blocks.append(block)

insertion = "\n".join(new_blocks) + "\n"

anchor = 'embedded_instances {\n  id: "wall_1"'
anchor_pos = content.find(anchor)
assert anchor_pos != -1
content = content[:anchor_pos] + insertion + content[anchor_pos:]

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("new floor tile count added:", len(new_blocks))
print("total nodes now, 'embedded_instances {' count:", content.count("embedded_instances {"))
print("boundary occurrences remaining:", content.count('"boundary"'))
print("file length:", len(content))
