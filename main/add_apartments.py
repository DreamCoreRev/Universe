BAK_PATH = "main.collection.bak"   # pristine pre-enlargement 3x3 room
PATH = "main.collection"           # current file to extend

with open(BAK_PATH, "r", encoding="utf-8") as f:
    bak = f.read()
with open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

assert 'id: "studio_floor"' not in content, "studio preset already added"
assert 'id: "room_controller"' not in content
assert 'id: "apartments"' not in content


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


# --- studio preset: the exact original 3x3 room, copied from the backup
# taken before the room was enlarged, just renamed so it can coexist with
# the current (loft) instances ---
STUDIO_SOURCE_IDS = [
    "floor", "floor_n1n1", "floor_n10", "floor_n11", "floor_0n1", "floor_01",
    "floor_1n1", "floor_10", "floor_11", "wall_1", "wall_2", "wall_3",
]

studio_blocks = []
for src_id in STUDIO_SOURCE_IDS:
    block, _, _ = extract_instance_block(bak, src_id)
    new_id = "studio_" + src_id
    block = block.replace('id: "%s"' % src_id, 'id: "%s"' % new_id, 1)
    studio_blocks.append(block)

studio_insertion = "\n".join(studio_blocks) + "\n"

# --- room_controller: plain script-only game object ---
room_controller_block = r'''embedded_instances {
  id: "room_controller"
  data: "components {\n"
  "  id: \"room_controller\"\n"
  "  component: \"/main/room_controller.script\"\n"
  "}\n"
  ""
  position {
    x: 0.0
    y: 0.0
  }
}
'''

# --- apartments: the room-picker GUI, same pattern as the furniture catalog ---
apartments_block = r'''embedded_instances {
  id: "apartments"
  data: "components {\n"
  "  id: \"apartments\"\n"
  "  component: \"/main/apartments.gui\"\n"
  "}\n"
  ""
  position {
    x: 0.0
    y: 0.0
  }
}
'''

for chunk in (studio_insertion, room_controller_block, apartments_block):
    assert chunk.count("{") == chunk.count("}"), chunk

anchor = 'embedded_instances {\n  id: "hud"'
anchor_pos = content.find(anchor)
assert anchor_pos != -1

insertion = studio_insertion + room_controller_block + apartments_block
content = content[:anchor_pos] + insertion + content[anchor_pos:]

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("studio blocks added:", len(studio_blocks))
print("file length:", len(content))
