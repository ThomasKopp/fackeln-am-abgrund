"""Check migrated content fidelity, routes, CMS files and media before deployment."""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

import build


class Page(HTMLParser):
    def __init__(self, text: str):
        super().__init__()
        self.text: list[str] = []
        self.links: list[str] = []
        self.ids: set[str] = set()
        self.tags = collections.Counter()
        self.feed(text)

    def handle_data(self, data: str) -> None:
        self.text.append(data)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        self.tags[tag] += 1
        if attributes.get("id"):
            self.ids.add(str(attributes["id"]))
        if tag in ("a", "img", "script", "link"):
            url = attributes.get("src", attributes.get("href", ""))
            if url:
                self.links.append(str(url))


def walk(node: dict):
    yield node
    for child in node.get("nodes", []):
        yield from walk(child)


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-missing-media", action="store_true")
    parser.add_argument("--base", default="/fackeln-am-abgrund")
    args = parser.parse_args()

    pages = {path: Page(path.read_text(encoding="utf-8")) for path in build.OUT.rglob("*.html")}
    errors: list[str] = []
    missing_media: set[str] = set()
    text_nodes = 0
    archives = [json.loads(path.read_text(encoding="utf-8")) for path in (build.ROOT / "content" / "posts").glob("*.json")]

    assert len(archives) == 19, "Expected all 19 original Wix JSON exports in content/posts"
    assert len(build.all_posts) >= 19, "Expected at least the 19 migrated posts"
    assert len({str(post["slug"]) for post in build.all_posts}) == len(build.all_posts), "Duplicate post slug"
    assert len({path.name for path in (build.ROOT / "content" / "posts").glob("*.md")}) == len(build.all_posts)
    assert (build.OUT / "admin" / "index.html").exists(), "Missing Decap CMS entry page"
    assert (build.OUT / "admin" / "config.yml").exists(), "Missing Decap CMS configuration"

    migrated = {str(post.get("wix_id")): post for post in build.all_posts if post.get("wix_id")}
    for archived in archives:
        if archived["id"] not in migrated:
            errors.append("No migrated Markdown post for Wix id " + archived["id"])
            continue
        post = migrated[archived["id"]]
        if post["slug"] != archived["slug"]:
            errors.append("Changed legacy slug: " + archived["slug"])
        if post.get("published", True) is False:
            errors.append("Migrated post unexpectedly unpublished: " + archived["slug"])
            continue
        path = build.OUT / "post" / str(post["slug"]) / "index.html"
        parsed = pages[path]
        nodes = [item for node in archived["richContent"]["nodes"] for item in walk(node)]
        actual = normalized(" ".join(parsed.text))
        for node in nodes:
            if node["type"] == "TEXT":
                text_nodes += 1
                expected = normalized(node["textData"]["text"])
                if expected and expected not in actual:
                    errors.append("Missing text in " + archived["slug"] + ": " + expected[:60])
        expected_images = sum(node["type"] == "IMAGE" for node in nodes)
        expected_tables = sum(node["type"] == "TABLE" for node in nodes)
        if parsed.tags["figure"] != expected_images:
            errors.append(f'Image count differs in {archived["slug"]}: {parsed.tags["figure"]} != {expected_images}')
        if parsed.tags["table"] != expected_tables:
            errors.append(f'Table count differs in {archived["slug"]}: {parsed.tags["table"]} != {expected_tables}')

    for path, parsed in pages.items():
        if "admin" not in path.parts and parsed.tags["h1"] != 1:
            errors.append("Expected one h1 in " + str(path))
        for url in parsed.links:
            split = urlsplit(url)
            if split.scheme or split.netloc:
                continue
            relative = unquote(split.path)
            if relative.startswith(args.base + "/"):
                relative = relative[len(args.base) + 1 :]
            elif relative.startswith("/"):
                errors.append("Wrong base: " + url)
                continue
            if not relative:
                destination = build.OUT / "index.html" if split.path else path
            else:
                destination = build.OUT / relative
            if destination.is_dir():
                destination = destination / "index.html"
            if not destination.exists():
                if "/assets/" in url:
                    missing_media.add(url)
                else:
                    errors.append("Missing route " + url)
            elif split.fragment and destination in pages and unquote(split.fragment) not in pages[destination].ids:
                errors.append("Missing anchor " + url)

    if missing_media and not args.allow_missing_media:
        errors.append(f"{len(missing_media)} missing image files")
    report = {
        "published_posts": len(build.posts),
        "content_files": len(build.all_posts),
        "wix_originals": len(archives),
        "pages": len(pages),
        "text_nodes_checked": text_nodes,
        "missing_media": len(missing_media),
        "errors": errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
