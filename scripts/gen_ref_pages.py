"""Generate the code reference pages and navigation."""

import pathlib

import mkdocs_gen_files


def gen_files(source: pathlib.Path) -> None:
    for path in sorted(source.rglob("*.py")):
        module_path = path.relative_to(source).with_suffix("")
        doc_path = path.relative_to(source).with_suffix(".md")
        full_doc_path = pathlib.Path("reference", doc_path)

        parts = tuple(module_path.parts)
        if module_path.name == "__main__":
            continue

        if module_path.name in ("api", "routines"):
            continue

        if module_path.name == "__init__":
            parts = parts[:-1]
            full_doc_path = full_doc_path.with_name("index.md")

        with mkdocs_gen_files.open(full_doc_path, "w") as fd:
            ident = ".".join(parts)
            fd.write(f"::: {ident}")

        mkdocs_gen_files.set_edit_path(full_doc_path, path.relative_to(root))


root = pathlib.Path(__file__).parent.parent
src = root / "src"
gen_files(src)
