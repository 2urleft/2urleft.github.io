import frontmatter
from jinja2 import Environment, FileSystemLoader, select_autoescape
import pathspec
import markdown
from markupsafe import Markup
import json

import os
import sys
import pathlib
import shutil
import tomllib

convert = markdown.Markdown(extensions=["fenced_code", "tables", "codehilite", "toc", "sane_lists"])

def render(txt):
    html = Markup(convert.convert(txt))
    convert.reset()
    return html

def walk_src(src, dest):
    config_path = os.path.join(src, "config.toml")
    config = {"settings": {}}
    if os.path.exists(config_path):
        with open(config_path, "rb") as f:
            config = tomllib.load(f)

    env = Environment(
        loader=FileSystemLoader(os.path.join(src, (config.get("settings").get("includes_folder") or "_includes"))),
        autoescape=select_autoescape(["html"])
    )

    root = pathlib.Path(src)
    ignore = os.path.join(root, ".ssignore")
    spec = pathspec.PathSpec([])

    if os.path.exists(ignore):
        with open(ignore, encoding='utf-8') as f:
            spec = pathspec.PathSpec.from_lines("gitignore", f)

    for path, subdirs, files in os.walk(root):
        path = pathlib.Path(path)
        rel_dir = os.path.relpath(path, root)

        subdirs[:] = [ # pruning subdirectories that match in .ssignore
            d for d in subdirs if not spec.match_file(os.path.join(rel_dir, d))
        ]

        default_file = os.path.join(path, "def.json")

        for file in files:
            rel_file = os.path.join(rel_dir, file)
            if spec.match_file(rel_file): continue # skips
            full_path = os.path.join(path, file)
            
            if file.endswith('.md'):
                if not os.path.exists(default_file):
                    default_metadata = "\0"
                else:
                    with open(default_file, encoding="utf-8") as f:
                        default_metadata = json.loads(f.read())

                with open(full_path, encoding='utf-8') as f:
                    loaded_file = frontmatter.load(f)
                    file_metadata = loaded_file.metadata
                    content = loaded_file.content

                    if default_metadata != "\0":
                        default_metadata |= file_metadata
                    else:
                        default_metadata = file_metadata
                    # use default_metadata for the rest
                    print(default_metadata)

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
                with open(out_path, "w", encoding='utf-8') as o:
                    o.write(html)
            else:
                out_path = pathlib.Path(os.path.join(dest, rel_dir, file))
                out_path.parent.mkdir(parents=True, exist_ok=True)

                copied_file = shutil.copy2(full_path, out_path)
                print(copied_file)

def main(args):
    if len(args) != 3:
        print(f"usage: {args[0]} <src> <dest>")
        return 1
    
    if os.path.exists(args[2]):
        shutil.rmtree(args[2])
    os.mkdir(args[2])

    walk_src(args[1], args[2])
    return 0

if __name__ == "__main__":
    # small cli
    main(sys.argv)