"""Build the independent static copy and Decap-managed Markdown posts."""

from __future__ import annotations

import argparse
import html
import json
import pathlib
import re
import shutil
import urllib.request
from urllib.parse import quote, unquote, urlsplit

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "site"
SOURCE = "https://tkopp37.wixsite.com/fackeln-am-abgrund"
PUBLIC_SITE = "https://thomaskopp.github.io/fackeln-am-abgrund"
PRODUCTION_BASE = "/fackeln-am-abgrund"
BASE = ""
esc = lambda value: html.escape(str(value), quote=True)

HOME_DEFAULTS = {
    "browser_title": "Shadowdark Rollenspielgruppe",
    "meta_description": "Unsere Shadowdark-Kampagne: Sessions und Hintergrund.",
    "hero_title": "Fackeln am Abgrund",
    "hero_subtitle": "Tauche ein in die Welt des Shadowdark!",
    "hero_image": "/assets/860736_689a1b6e45ca4d3c8942cea5d9d79b41~mv2.webp",
    "hero_image_alt": "Zwei gekreuzte Fackeln über dem Abgrund",
    "sessions_title": "Sessions",
    "sessions_description": "Hier entfaltet sich die Geschichte unserer Abenteurer - bejubelt die Lebenden und ehret die Toten!",
    "background_title": "Hintergrund",
    "background_description": "Hier sind Hintergrundinformationen zu finden.",
}


def load_homepage() -> dict[str, str]:
    path = ROOT / "content" / "settings" / "homepage.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    homepage = {**HOME_DEFAULTS, **data}
    for field in HOME_DEFAULTS:
        if not isinstance(homepage.get(field), str) or not homepage[field].strip():
            raise ValueError(f"Homepage field must be a non-empty string: {field}")
    return homepage


def read_frontmatter(path: pathlib.Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if lines and lines[0].strip() == "{":
        metadata, end = json.JSONDecoder().raw_decode(text)
        return metadata, text[end:].strip()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"Missing front matter in {path}")
    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration as error:
        raise ValueError(f"Unclosed front matter in {path}") from error
    data: dict[str, object] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"Unsupported front matter line in {path}: {line}")
        key, raw = line.split(":", 1)
        raw = raw.strip()
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            value = raw.strip("'\"")
        data[key.strip()] = value
    return data, "\n".join(lines[end + 1 :]).strip()


def load_posts() -> list[dict]:
    loaded = []
    for path in (ROOT / "content" / "posts").glob("*.md"):
        metadata, body = read_frontmatter(path)
        required = {"title", "slug", "date", "excerpt", "category"}
        missing = sorted(required - metadata.keys())
        if missing:
            raise ValueError(f"Missing fields in {path}: {', '.join(missing)}")
        post = dict(metadata)
        post["body"] = body
        post["source_path"] = path
        loaded.append(post)
    return sorted(loaded, key=lambda post: str(post["date"]), reverse=True)


all_posts = load_posts()
posts = [post for post in all_posts if post.get("published", True) is not False]
slugs = {str(post["slug"]) for post in all_posts}
homepage = load_homepage()


def local(path: str = "") -> str:
    return BASE + "/" + path.lstrip("/")


def asset_url(url: str) -> str:
    decoded = unquote(str(url))
    for prefix in (PRODUCTION_BASE + "/assets/", "/assets/"):
        if decoded.startswith(prefix):
            return local("assets/" + quote(decoded[len(prefix) :], safe="/._~-"))
    return str(url)


def link(url: str) -> str:
    url = asset_url(url)
    if url.startswith(SOURCE):
        tail = unquote(url[len(SOURCE) :]).rstrip("/")
        if tail == "" or tail == "/blank" or (tail.startswith("/post/") and tail[6:] in slugs):
            return local(quote(tail.lstrip("/"), safe="/") + "/") if tail else local()
    if url.startswith(PRODUCTION_BASE + "/"):
        return local(url[len(PRODUCTION_BASE) + 1 :])
    return url if urlsplit(url).scheme in ("https", "http", "mailto") or url.startswith(("#", BASE + "/")) else "#"


def image_tag(url: str, alt: str = "", lazy: bool = True) -> str:
    return f'<img src="{esc(asset_url(url))}" alt="{esc(alt)}" loading="{"lazy" if lazy else "eager"}" decoding="async">'


def render_inline(text: str) -> str:
    tokens: list[str] = []

    def token(value: str) -> str:
        tokens.append(value)
        return f"\x00{len(tokens) - 1}\x00"

    def image(match: re.Match) -> str:
        return token(image_tag(match.group(2), match.group(1)))

    def hyperlink(match: re.Match) -> str:
        return token(f'<a href="{esc(link(match.group(2)))}">{render_inline(match.group(1))}</a>')

    def code(match: re.Match) -> str:
        return token(f"<code>{esc(match.group(1))}</code>")

    text = re.sub(r"!\[([^]]*)\]\((\S+?)(?:\s+[\"'][^\"']*[\"'])?\)", image, text)
    text = re.sub(r"\[([^]]+)\]\(([^)]+)\)", hyperlink, text)
    text = re.sub(r"`([^`]+)`", code, text)
    value = html.escape(text, quote=False)
    value = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", value)
    value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", value)
    value = re.sub(r"&lt;u&gt;(.*?)&lt;/u&gt;", r"<u>\1</u>", value)
    value = value.replace("  \n", "<br>").replace("\n", " ")
    for index, item in enumerate(tokens):
        value = value.replace(f"\x00{index}\x00", item)
    return value


def is_block_start(line: str) -> bool:
    stripped = line.strip()
    return bool(
        re.match(r"^(#{1,6})\s+", stripped)
        or re.match(r"^(?:[-*+] |\d+[.)] )", stripped)
        or stripped.startswith(("> ", "```", "~~~", "!["))
        or stripped in {"---", "***", "___"}
        or (stripped.startswith("|") and stripped.endswith("|"))
    )


def render_markdown(markdown: str) -> str:
    lines = markdown.replace("\r\n", "\n").split("\n")
    output: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            index += 1
            continue
        fence = re.match(r"^(```|~~~)(.*)$", stripped)
        if fence:
            marker, language = fence.groups()
            code_lines = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith(marker):
                code_lines.append(lines[index])
                index += 1
            index += index < len(lines)
            class_name = f' class="language-{esc(language.strip())}"' if language.strip() else ""
            output.append(f"<pre><code{class_name}>{esc(chr(10).join(code_lines))}</code></pre>")
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading:
            level = min(6, max(2, len(heading.group(1))))
            output.append(f"<h{level}>{render_inline(heading.group(2))}</h{level}>")
            index += 1
            continue
        if stripped in {"---", "***", "___"}:
            output.append("<hr>")
            index += 1
            continue
        if stripped.startswith("!["):
            match = re.fullmatch(r"!\[([^]]*)\]\((\S+?)(?:\s+[\"'][^\"']*[\"'])?\)", stripped)
            if match:
                url = asset_url(match.group(2))
                output.append(f'<figure><a href="{esc(url)}">{image_tag(match.group(2), match.group(1))}</a></figure>')
                index += 1
                continue
        if stripped.startswith("|") and stripped.endswith("|") and index + 1 < len(lines):
            separator = lines[index + 1].strip()
            if re.fullmatch(r"\|(?:\s*:?-+:?\s*\|)+", separator):
                rows = []
                row_index = 0
                while index < len(lines) and lines[index].strip().startswith("|") and lines[index].strip().endswith("|"):
                    current = lines[index].strip()
                    if row_index != 1:
                        rows.append([cell.strip().replace("\\|", "|") for cell in current[1:-1].split("|")])
                    row_index += 1
                    index += 1
                if len(rows) >= 2:
                    head = "".join(f"<th>{render_inline(cell)}</th>" for cell in rows[0])
                    body = "".join("<tr>" + "".join(f"<td>{render_inline(cell)}</td>" for cell in row) + "</tr>" for row in rows[1:])
                    output.append(f'<div class="table-scroll"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')
                continue
        list_match = re.match(r"^\s*(?P<marker>[-*+]|\d+[.)])\s+(?P<text>.+)$", line)
        if list_match:
            ordered = list_match.group("marker")[0].isdigit()
            tag = "ol" if ordered else "ul"
            items = []
            while index < len(lines):
                current = re.match(r"^\s*(?P<marker>[-*+]|\d+[.)])\s+(?P<text>.+)$", lines[index])
                if not current or current.group("marker")[0].isdigit() != ordered:
                    break
                item_lines = [current.group("text")]
                index += 1
                while index < len(lines) and lines[index].strip() and not re.match(r"^\s*(?:[-*+]|\d+[.)])\s+", lines[index]):
                    item_lines.append(lines[index].strip())
                    index += 1
                items.append("<li>" + render_inline("\n".join(item_lines)) + "</li>")
                while index < len(lines) and not lines[index].strip():
                    index += 1
            output.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
            continue
        if stripped.startswith("> "):
            quote_lines = []
            while index < len(lines) and lines[index].strip().startswith("> "):
                quote_lines.append(lines[index].strip()[2:])
                index += 1
            output.append("<blockquote><p>" + render_inline("\n".join(quote_lines)) + "</p></blockquote>")
            continue
        paragraph = [stripped]
        index += 1
        while index < len(lines) and lines[index].strip() and not is_block_start(lines[index]):
            paragraph.append(lines[index].strip())
            index += 1
        output.append("<p>" + render_inline("\n".join(paragraph)) + "</p>")
    return "".join(output)


def page(title: str, body: str, canonical: str = PUBLIC_SITE + "/", description: str = "Unsere Shadowdark-Kampagne: Sessions und Hintergrund.") -> str:
    return f'''<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | Fackeln am Abgrund</title><meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(canonical)}"><link rel="stylesheet" href="{local('style.css')}">
</head><body><a class="skip" href="#inhalt">Zum Inhalt</a><header><a class="brand" href="{local()}">Fackeln am Abgrund</a>
<nav aria-label="Hauptnavigation"><a href="{local()}#sessions">Sessions</a><a href="{local()}#hintergrund">Hintergrund</a><a href="{local('admin/')}">Bearbeiten</a><a href="{SOURCE}">Wix-Original ↗</a></nav></header>
<main id="inhalt">{body}</main><footer><a href="mailto:t.kopp@gmx.de">t.kopp(at)gmx.de</a><a href="{local('blank/')}">Datenschutzerklärung</a><span>Shadowdark · Fackeln am Abgrund</span></footer>
<script src="{local('search.js')}" defer></script></body></html>'''


def write(path: str, text: str) -> None:
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def card(post: dict) -> str:
    image = image_tag(str(post.get("featured_image", "")), str(post.get("featured_image_alt") or post["title"])) if post.get("featured_image") else ""
    excerpt = str(post["excerpt"])
    return f'<article class="card" data-search="{esc(str(post["title"]) + " " + excerpt)}"><a href="{local("post/" + quote(str(post["slug"])) + "/")}">{image}<div><time datetime="{esc(post["date"])}">{esc(str(post["date"])[:10])}</time><h3>{esc(post["title"])}</h3><p>{esc(excerpt[:180])}{"…" if len(excerpt) > 180 else ""}</p></div></a></article>'


def copy_media(offline: bool) -> list[dict]:
    cache = ROOT / "assets"
    cache.mkdir(exist_ok=True)
    missing = []
    for media_id in json.loads((ROOT / "content" / "media.json").read_text(encoding="utf-8")):
        destination = cache / media_id
        if not destination.exists() and not offline:
            try:
                with urllib.request.urlopen("https://static.wixstatic.com/media/" + quote(media_id), timeout=60) as response:
                    data = response.read()
                    if not response.headers.get("Content-Type", "").startswith("image/") or len(data) < 100:
                        raise ValueError("Invalid image")
                destination.write_bytes(data)
            except Exception as error:
                missing.append({"image": media_id, "error": str(error)})
        elif not destination.exists():
            missing.append({"image": media_id, "error": "offline"})
    if cache.exists():
        shutil.copytree(cache, OUT / "assets", dirs_exist_ok=True)
    (ROOT / "media-status.json").write_text(json.dumps(missing, ensure_ascii=False, indent=2), encoding="utf-8")
    if missing and not offline:
        raise RuntimeError(f"{len(missing)} images missing; deployment aborted. See media-status.json")
    return missing


def main() -> None:
    global BASE
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=PRODUCTION_BASE)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    BASE = args.base.rstrip("/")
    if BASE and not re.fullmatch(r"/[A-Za-z0-9._/-]+", BASE):
        raise ValueError("Invalid base path")
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    missing = copy_media(args.offline)
    shutil.copytree(ROOT / "static", OUT, dirs_exist_ok=True)
    intro = f'<section class="hero"><h1>{esc(homepage["hero_title"])}</h1>{image_tag(homepage["hero_image"], homepage["hero_image_alt"], False)}<h2>{esc(homepage["hero_subtitle"])}</h2></section>'
    intro += '<div class="search" hidden><label for="suche">Beiträge durchsuchen</label><input id="suche" type="search" placeholder="Titel oder Stichwort …"><p id="suchstatus" role="status"></p></div>'
    groups = [
        ("sessions", homepage["sessions_title"], homepage["sessions_description"]),
        ("hintergrund", homepage["background_title"], homepage["background_description"]),
    ]
    for key, title, description in groups:
        group = [post for post in posts if post["category"] == key]
        intro += f'<section id="{key}" class="collection"><h2>{title}</h2><p>{description}</p><div class="grid">' + "".join(card(post) for post in group) + "</div></section>"
    write("index.html", page(homepage["browser_title"], intro, description=homepage["meta_description"]))
    for post in posts:
        body = render_markdown(str(post["body"]))
        words = len(re.findall(r"\w+", str(post["body"]), re.UNICODE))
        minutes = max(1, round(words / 200))
        original = str(post.get("original_url", "")).strip()
        canonical = original or f'{PUBLIC_SITE}/post/{quote(str(post["slug"]))}/'
        aside = f'<aside><a href="{esc(original)}">Originalbeitrag und Kommentare auf Wix ↗</a></aside>' if original else ""
        article = f'<article class="post"><a href="{local()}">← Alle Beiträge</a><h1>{esc(post["title"])}</h1><time datetime="{esc(post["date"])}">{esc(str(post["date"])[:10])} · {minutes} Min. Lesezeit</time><div class="prose">{body}</div>{aside}</article>'
        write(f'post/{post["slug"]}/index.html', page(str(post["title"]), article, canonical, str(post["excerpt"])))
    privacy = (ROOT / "content" / "privacy.html").read_text(encoding="utf-8")
    write("blank/index.html", page("Datenschutzerklärung", '<article class="post prose"><h1>Datenschutz</h1>' + privacy + "</article>", SOURCE + "/blank"))
    write("404.html", page("Seite nicht gefunden", f'<article class="post"><h1>Diese Seite gibt es hier nicht.</h1><a href="{local()}">Zur Startseite</a></article>'))
    write(".nojekyll", "")
    print(f"Built {len(posts)} published posts ({len(all_posts) - len(posts)} drafts), homepage, privacy, admin and 404. Missing media: {len(missing)}.")


if __name__ == "__main__":
    main()
