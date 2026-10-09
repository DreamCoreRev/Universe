PATH = "main.collection"

with open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

assert 'id: "camera"' not in content, "a camera instance already exists"

# Built using a raw string so every backslash below is literal (no Python
# escape processing at all) -- this exactly mirrors the byte-for-byte
# pattern confirmed by hexdumping an existing collisionobject block in this
# same file: outer-level fields (id/type/data open+close quotes, and the
# embedded_components closing brace) use ONE backslash before \n or \" ;
# the lines *inside* the twice-nested "data" string value use TWO
# backslashes before \n, since that \n must survive two string-literal
# parses (the GO's own data field, then embedded_components' data field).
camera_block = r'''embedded_instances {
  id: "camera"
  data: "components {\n"
  "  id: \"camera_script\"\n"
  "  component: \"/main/camera.script\"\n"
  "}\n"
  "embedded_components {\n"
  "  id: \"camera\"\n"
  "  type: \"camera\"\n"
  "  data: \"aspect_ratio: 1.0\\n"
  "fov: 0.7854\\n"
  "near_z: -1.0\\n"
  "far_z: 1.0\\n"
  "auto_aspect_ratio: 1\\n"
  "orthographic_projection: 1\\n"
  "orthographic_zoom: 1.0\\n"
  "\"\n"
  "}\n"
  ""
  position {
    x: 480.0
    y: 300.0
  }
}
'''

# sanity: braces inside this chunk must balance like the other instance
# blocks do (string-embedded braces are always internally balanced here)
assert camera_block.count("{") == camera_block.count("}"), (
    camera_block.count("{"), camera_block.count("}")
)

anchor = 'embedded_instances {\n  id: "wall_1"'
anchor_pos = content.find(anchor)
assert anchor_pos != -1

content = content[:anchor_pos] + camera_block + content[anchor_pos:]

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("inserted camera instance, file length:", len(content))
