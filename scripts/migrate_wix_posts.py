"""Convert the preserved Wix Rich Content exports to Decap-friendly Markdown."""

from __future__ import annotations

import argparse
import html
import json
import pathlib
import re
import shutil
from urllib.parse import quote, unquote

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "content" / "posts"
ARCHIVE_DIR = ROOT / "content" / "wix-archive"
SITE_PREFIX = "/fackeln-am-abgrund"
WIX_BASE = "https://tkopp37.wixsite.com/fackeln-am-abgrund"


def plain_text(node: dict) -> str:
    if node["type"] == "TEXT":
        return node["textData"]["text"]
    return "".join(plain_text(child) for child in node.get("nodes", []))


def inline(node: dict) -> str:
    if node["type"] != "TEXT":
        return "".join(inline(child) for child in node.get("nodes", []))
    value = node["textData"]["text"].replace("\\", "\\\\")
    for decoration in node["textData"].get("decorations", []):
        kind = decoration["type"]
        if kind == "BOLD":
            value = f"**{value}**"
        elif kind == "ITALIC":
            value = f"*{value}*"
        elif kind == "SKETCH":
            value = f"<u>{html.escape(value)}</u>"
        elif kind == "LINK":
            link = decoration["linkData"]["link"]
            target = link.get("url") or ("#" + link.get("anchor", ""))
            if target.startswith(WIX_BASE):
                tail = unquote(target[len(WIX_BASE) :]).rstrip("/")
                if tail in {"", "/blank"} or tail.startswith("/post/"):
                    target = SITE_PREFIX + quote(tail, safe="/#") + ("/" if tail else "")
            value = f"[{value}]({target})"
        else:
            raise ValueError(f"Unsupported Wix decoration: {kind}")
    return value


def table_markdown(node: dict) -> str:
    rows = []
    for row in node.get("nodes", []):
        cells = [re.sub(r"\s+", " ", plain_text(cell)).strip().replace("|", "\\|") for cell in row.get("nodes", [])]
        rows.append(cells)
    if not rows:
        return ""
    width = len(rows[0])
    if not width or any(len(row) != width for row in rows):
        raise ValueError("Wix table is not rectangular")
    rendered = ["| " + " | ".join(row) + " |" for row in rows]
    rendered.insert(1, "| " + " | ".join("---" for _ in range(width)) + " |")
    return "\n".join(rendered)


def blocks(nodes: list[dict], indent: int = 0) -> list[str]:
    result: list[str] = []
    for node in nodes:
        kind = node["type"]
        if kind == "HEADING":
            level = min(6, max(2, int(node["headingData"]["level"])))
            result.append("#" * level + " " + inline(node).strip())
        elif kind in {"PARAGRAPH", "CAPTION"}:
            text = inline(node).strip()
            if text:
                result.append(text)
        elif kind in {"BULLETED_LIST", "ORDERED_LIST"}:
            ordered = kind == "ORDERED_LIST"
            items = []
            for index, item in enumerate(node.get("nodes", []), 1):
                item_blocks = blocks(item.get("nodes", []), indent + 1)
                if not item_blocks:
                    continue
                marker = f"{index}." if ordered else "-"
                padding = "    " * (indent + 1)
                joined = "\n\n".join(item_blocks).replace("\n", "\n" + padding)
                items.append("  " * indent + marker + " " + joined)
            if items:
                result.append("\n".join(items))
        elif kind == "LIST_ITEM":
            result.extend(blocks(node.get("nodes", []), indent))
        elif kind == "IMAGE":
            data = node["imageData"]
            media_id = data["image"]["src"]["id"]
            alt = data.get("altText") or data.get("caption") or ""
            result.append(f"![{alt}]({SITE_PREFIX}/assets/{quote(media_id)})")
            caption = plain_text(node).strip() or data.get("caption", "").strip()
            if caption:
                result.append(f"*{caption}*")
        elif kind == "TABLE":
            result.append(table_markdown(node))
        elif kind in {"TABLE_ROW", "TABLE_CELL", "TEXT"}:
            raise ValueError(f"Unexpected top-level Wix node: {kind}")
        else:
            raise ValueError(f"Unsupported Wix node: {kind}")
    return result


def convert(path: pathlib.Path, force: bool = False) -> pathlib.Path | None:
    post = json.loads(path.read_text(encoding="utf-8"))
    title = post["title"]
    category = "sessions" if title.startswith("Session") else "hintergrund"
    media = post.get("media", {}).get("wixMedia", {}).get("image", {})
    original_url = post.get("url", {}).get("base", WIX_BASE) + post.get("url", {}).get("path", "/post/" + post["slug"])
    frontmatter = {
        "title": title,
        "slug": post["slug"],
        "date": post["firstPublishedDate"],
        "updated": post.get("lastPublishedDate", post["firstPublishedDate"]),
        "excerpt": post["excerpt"],
        "category": category,
        "published": True,
        "featured_image": SITE_PREFIX + "/assets/" + quote(media["id"]) if media.get("id") else "",
        "featured_image_alt": post.get("media", {}).get("altText") or title,
        "original_url": original_url,
        "wix_id": post["id"],
    }
    body = "\n\n".join(blocks(post["richContent"]["nodes"]))
    output = SOURCE_DIR / f"{post['slug']}.md"
    if output.exists() and not force:
        return None
    output.write_text(json.dumps(frontmatter, ensure_ascii=False, indent=2) + "\n\n" + body + "\n", encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Regenerate existing Markdown files")
    args = parser.parse_args()
    sources = sorted(SOURCE_DIR.glob("*.json")) or sorted(ARCHIVE_DIR.glob("*.json"))
    if not sources:
        raise SystemExit("No Wix JSON files found in content/posts")
    outputs = [output for path in sources if (output := convert(path, args.force))]
    for path in sources:
        if path.parent == ARCHIVE_DIR:
            shutil.copy2(path, SOURCE_DIR / path.name)
    if ARCHIVE_DIR.exists():
        shutil.rmtree(ARCHIVE_DIR)
    print(f"Created {len(outputs)} missing Markdown posts; original JSON preserved in {SOURCE_DIR.relative_to(ROOT)}.")


if __name__ == "__main__":
    main()
