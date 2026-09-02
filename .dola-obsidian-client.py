def create_from_template(template_name, data):
    template = open(f'Templates/{template_name}.md').read()
    content = template.format(**data)
    # POST content ไป Obsidian
