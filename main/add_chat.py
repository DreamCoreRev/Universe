PATH = "main.collection"

with open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

assert 'id: "chat"' not in content, "a chat instance already exists"

chat_block = r'''embedded_instances {
  id: "chat"
  data: "components {\n"
  "  id: \"chat\"\n"
  "  component: \"/main/chat.gui\"\n"
  "}\n"
  ""
  position {
    x: 0.0
    y: 0.0
  }
}
'''

assert chat_block.count("{") == chat_block.count("}")

anchor = 'embedded_instances {\n  id: "hud"'
anchor_pos = content.find(anchor)
assert anchor_pos != -1

content = content[:anchor_pos] + chat_block + content[anchor_pos:]

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("inserted chat instance, file length:", len(content))
