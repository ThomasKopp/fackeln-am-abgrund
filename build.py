"""Build the independent static copy. Python 3.12+, standard library only."""
import argparse, html, json, pathlib, re, shutil, urllib.request
from urllib.parse import quote, unquote, urlsplit

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / 'site'
SOURCE = 'https://tkopp37.wixsite.com/fackeln-am-abgrund'
esc = lambda s: html.escape(str(s), quote=True)
posts = sorted([json.loads(p.read_text(encoding='utf-8')) for p in (ROOT/'content/posts').glob('*.json')], key=lambda p:p['firstPublishedDate'], reverse=True)
slugs = {p['slug'] for p in posts}
BASE = ''

def local(path=''):
    return BASE + '/' + path.lstrip('/')

def link(url):
    if url.startswith(SOURCE):
        tail = unquote(url[len(SOURCE):]).rstrip('/')
        if tail == '' or tail == '/blank' or (tail.startswith('/post/') and tail[6:] in slugs):
            return local(quote(tail.lstrip('/'), safe='/') + '/') if tail else local()
    return url if urlsplit(url).scheme in ('https','http','mailto') or url.startswith('#') else '#'

def image_id(p):
    return p.get('media',{}).get('wixMedia',{}).get('image',{}).get('id')

def image_tag(mid,alt='',lazy=True):
    return f'<img src="{esc(local("assets/"+quote(mid)))}" alt="{esc(alt)}" loading="{"lazy" if lazy else "eager"}" decoding="async">'

def render(n):
    t=n['type']; children=''.join(render(c) for c in n.get('nodes',[]))
    ident=f' id="{esc(n["id"])}"' if n.get('id') else ''
    if t=='TEXT':
        s=esc(n['textData']['text']).replace('\n','<br>')
        for d in n['textData'].get('decorations',[]):
            if d['type']=='BOLD': s='<strong>'+s+'</strong>'
            elif d['type']=='ITALIC': s='<em>'+s+'</em>'
            elif d['type']=='SKETCH': s='<u>'+s+'</u>'
            elif d['type']=='LINK':
                l=d['linkData']['link']; s=f'<a href="{esc(link(l.get("url","#"+l.get("anchor",""))))}">'+s+'</a>'
            else: raise ValueError('Unsupported decoration '+d['type'])
        return s
    if t=='IMAGE':
        d=n['imageData']; mid=d['image']['src']['id']
        caption=children or ('<figcaption>'+esc(d['caption'])+'</figcaption>' if d.get('caption') else '')
        return f'<figure{ident}><a href="{esc(local("assets/"+quote(mid)))}">'+image_tag(mid,d.get('altText',d.get('caption','')))+f'</a>{caption}</figure>'
    tags={'PARAGRAPH':'p','CAPTION':'figcaption','BULLETED_LIST':'ul','ORDERED_LIST':'ol','LIST_ITEM':'li','TABLE':'table','TABLE_ROW':'tr','TABLE_CELL':'td'}
    if t=='HEADING': tag='h'+str(min(6,max(2,n['headingData']['level'])))
    else: tag=tags[t]
    result=f'<{tag}{ident}>{children}</{tag}>'
    return '<div class="table-scroll">'+result+'</div>' if t=='TABLE' else result

def page(title,body,canonical=SOURCE,description='Unsere Shadowdark-Kampagne: Sessions und Hintergrund.'):
    return f'''<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | Fackeln am Abgrund</title><meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(canonical)}"><link rel="stylesheet" href="{local('style.css')}">
</head><body><a class="skip" href="#inhalt">Zum Inhalt</a><header><a class="brand" href="{local()}">Fackeln am Abgrund</a>
<nav aria-label="Hauptnavigation"><a href="{local()}#sessions">Sessions</a><a href="{local()}#hintergrund">Hintergrund</a><a href="{SOURCE}">Wix-Original ↗</a></nav></header>
<main id="inhalt">{body}</main><footer><a href="mailto:t.kopp@gmx.de">t.kopp(at)gmx.de</a><a href="{local('blank/')}">Datenschutzerklärung</a><span>Shadowdark · Fackeln am Abgrund</span></footer>
<script src="{local('search.js')}" defer></script></body></html>'''

def write(path,text):
    p=OUT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')

def card(p):
    img=image_tag(image_id(p),p['media'].get('altText',p['title'])) if image_id(p) else ''
    return f'<article class="card" data-search="{esc(p["title"]+" "+p["excerpt"])}"><a href="{local("post/"+quote(p["slug"])+"/")}">{img}<div><time datetime="{p["firstPublishedDate"]}">{p["firstPublishedDate"][:10]}</time><h3>{esc(p["title"])}</h3><p>{esc(p["excerpt"][:180])}…</p></div></a></article>'

def download_media(offline):
    cache=ROOT/'assets';cache.mkdir(exist_ok=True);missing=[]
    for mid in json.loads((ROOT/'content/media.json').read_text(encoding='utf-8')):
        dest=cache/mid
        if not dest.exists() and not offline:
            try:
                with urllib.request.urlopen('https://static.wixstatic.com/media/'+quote(mid),timeout=60) as r:
                    data=r.read()
                    if not r.headers.get('Content-Type','').startswith('image/') or len(data)<100: raise ValueError('Invalid image')
                dest.write_bytes(data)
            except Exception as e: missing.append({'image':mid,'error':str(e)})
        elif not dest.exists(): missing.append({'image':mid,'error':'offline'})
        if dest.exists(): shutil.copy2(dest,OUT/'assets'/mid)
    (ROOT/'media-status.json').write_text(json.dumps(missing,ensure_ascii=False,indent=2),encoding='utf-8')
    if missing and not offline: raise RuntimeError(f'{len(missing)} images missing; deployment aborted. See media-status.json')
    return missing

def main():
    global BASE
    ap=argparse.ArgumentParser();ap.add_argument('--base',default='/fackeln-am-abgrund');ap.add_argument('--offline',action='store_true');args=ap.parse_args()
    BASE=args.base.rstrip('/')
    if BASE and not re.fullmatch(r'/[A-Za-z0-9._/-]+',BASE): raise ValueError('Invalid base path')
    OUT.mkdir(exist_ok=True);(OUT/'assets').mkdir(exist_ok=True)
    missing=download_media(args.offline)
    for name in ['style.css','search.js']:shutil.copy2(ROOT/'static'/name,OUT/name)
    intro=f'<section class="hero"><h1>Fackeln am Abgrund</h1>{image_tag("860736_689a1b6e45ca4d3c8942cea5d9d79b41~mv2.webp","Zwei gekreuzte Fackeln über dem Abgrund",False)}<h2>Tauche ein in die Welt des Shadowdark!</h2></section>'
    intro+='<div class="search" hidden><label for="suche">Beiträge durchsuchen</label><input id="suche" type="search" placeholder="Titel oder Stichwort …"><p id="suchstatus" role="status"></p></div>'
    for key,title,desc in [('sessions','Sessions','Hier entfaltet sich die Geschichte unserer Abenteurer - bejubelt die Lebenden und ehret die Toten!'),('hintergrund','Hintergrund','Hier sind Hintergrundinformationen zu finden.')]:
        group=[p for p in posts if p['title'].startswith('Session')==(key=='sessions')]
        intro+=f'<section id="{key}" class="collection"><h2>{title}</h2><p>{desc}</p><div class="grid">'+''.join(card(p) for p in group)+'</div></section>'
    write('index.html',page('Shadowdark Rollenspielgruppe',intro))
    for p in posts:
        body=''.join(render(n) for n in p['richContent']['nodes'])
        body=f'<article class="post"><a href="{local()}">← Alle Beiträge</a><h1>{esc(p["title"])}</h1><time datetime="{p["firstPublishedDate"]}">{p["firstPublishedDate"][:10]} · {p["minutesToRead"]} Min. Lesezeit</time><div class="prose">{body}</div><aside><a href="{SOURCE}/post/{quote(p["slug"])}">Originalbeitrag und Kommentare auf Wix ↗</a></aside></article>'
        write('post/'+p['slug']+'/index.html',page(p['title'],body,SOURCE+'/post/'+quote(p['slug']),p['excerpt']))
    privacy=(ROOT/'content/privacy.html').read_text(encoding='utf-8')
    write('blank/index.html',page('Datenschutzerklärung','<article class="post prose"><h1>Datenschutz</h1>'+privacy+'</article>',SOURCE+'/blank'))
    write('404.html',page('Seite nicht gefunden',f'<article class="post"><h1>Diese Seite gibt es hier nicht.</h1><a href="{local()}">Zur Startseite</a></article>'))
    write('.nojekyll','')
    print(f'Built {len(posts)} posts, homepage, privacy and 404. Missing media: {len(missing)}.')

if __name__=='__main__': main()
