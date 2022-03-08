import os
import re

INPUT_PATHNAME = "instruction-turker.html"
OUTPUT_PATH = os.path.join(
    '..',
    '..',
    'MTurkFrontend',
)
reg = re.compile(
    r'<h1 id="annotation-in-vidat">Annotation In Vidat</h1>([\s\S]+?)<h1 id="submit-in-mturk">Submit In MTurk</h1>'
)
img_src_reg = re.compile(r'<img src="(.+?)"')

# locd input
with open(INPUT_PATHNAME, 'r', encoding='utf8') as f:
    content = f.read()
content = reg.findall(content)[0]

# use raw.githubusercontent.com for img src
for img_src in img_src_reg.findall(content):
    content = content.replace(
        img_src, f'https://raw.githubusercontent.com/DavidZhang73/MTurkManagement/main/instruction/turker/{img_src}'
    )

# insert back to template
with open(os.path.join(OUTPUT_PATH, 'template.html'), 'r', encoding='utf8') as f:
    template = f.read()
with open(os.path.join(OUTPUT_PATH, 'index.html'), 'w', encoding='utf8') as f:
    f.write(template.replace("INSTRUCTION_TEMPLATE", content))
