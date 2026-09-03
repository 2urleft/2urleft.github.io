import frontmatter
from jinja2 import Environment, FileSystemLoader, select_autoescape
import pathspec
import markdown
from markupsafe import Markup
import json

import os
import sys
import pathlib

convert = markdown.Markdown(extensions=["fenced_code", "tables", "codehilite", "toc", "sane_lists"])

def render(txt):
    html = Markup(convert.convert(txt))
    convert.reset()
    return html

def walk_src(src, dest):
    env = Environment(
        loader=FileSystemLoader(os.path.join(src, "_includes")),
        autoescape=select_autoescape(["html"]),
    )

    root = pathlib.Path(src)
    ignore = os.path.join(root, ".ssignore")
    spec = pathspec.PathSpec([])

    if os.path.exists(ignore):
        with open(ignore) as f:
            spec = pathspec.PathSpec.from_lines("gitignore", f)

    for path, subdirs, files in os.walk(root):
        path = pathlib.Path(path)
        rel_dir = os.path.relpath(path, root)

        subdirs[:] = [ # pruning subdirectories that match in .ssignore
            d for d in subdirs if not spec.match_file(os.path.join(rel_dir, d))
        ]

        files[:] = [ # pruning non-markdown files
            f for f in files if f.endswith(".md")
        ]

        default_file = os.path.join(path, "def.json")

        if not os.path.exists(default_file):
            default_metadata = "\0"
        else:
            with open(default_file, encoding="utf-8-sig") as f:
                default_file = f.read()
            default_metadata = json.loads(default_file)

        for file in files:
            rel_file = os.path.join(rel_dir, file)
            if spec.match_file(rel_file): continue # skips
            full_path = os.path.join(path, file)

            with open(full_path, "r+") as f:
                loaded_file = frontmatter.load(f)
                file_metadata = loaded_file.metadata
                content = loaded_file.content

                if default_metadata != "\0":
                    default_metadata |= file_metadata
                else:
                    default_metadata = file_metadata
                # use default_metadata for the rest

                if default_metadata.get("layout") != None:
                    template = env.get_template(default_metadata["layout"])
                    del default_metadata["layout"]

                    html_content = render(content)

                    html = template.render(content=html_content,
                                        **default_metadata)
                else:
                    html = render(content)

            out_path = pathlib.Path(os.path.join(dest, rel_dir, pathlib.Path(file).with_suffix('.html')))
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "w") as o:
                o.write(html)  

if __name__ == "__main__":
    walk_src("../src", "../_site")