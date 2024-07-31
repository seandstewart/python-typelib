"""Generate the code reference pages and navigation."""

import pathlib

import mkdocs_gen_files


def gen_files(source: pathlib.Path) -> None:
    nav = mkdocs_gen_files.Nav()
    for path in sorted(source.rglob("*.py")):
        module_path = path.relative_to(source).with_suffix("")
        doc_path = path.relative_to(source).with_suffix(".md")
        full_doc_path = pathlib.Path("reference", doc_path)

        parts = tuple(module_path.parts)
        if module_path.name == "__main__":
            continue

        if module_path.name in ("api", "routines") and module_path.parent.name in (
            "marshal",
            "unmarshal",
        ):
            continue

        if module_path.name == "__init__":
            parts = parts[:-1]
            doc_path = doc_path.with_name("index.md")
            full_doc_path = full_doc_path.with_name("index.md")

        nav[parts] = doc_path.as_posix()

        with mkdocs_gen_files.open(full_doc_path, "w") as fd:
            ident = ".".join(parts)
            fd.write(f"::: {ident}")

        mkdocs_gen_files.set_edit_path(full_doc_path, path.relative_to(root))

    with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
        nav_file.writelines(nav.build_literate_nav())


root = pathlib.Path(__file__).parent.parent
src = root / "src"
gen_files(src)
