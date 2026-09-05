"""Check content fidelity, routes and media before deployment."""
import argparse, collections, html, json, pathlib, re
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import build

class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.text=[];self.links=[];self.ids=set();self.tags=collections.Counter();self.feed(text)
    def handle_data(self,d):self.text.append(d)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs);self.tags[tag]+=1
        if 'id' in a:self.ids.add(a['id'])
        if tag in ('a','img','script','link'):
            u=a.get('src',a.get('href',''))
            if u:self.links.append(u)

def walk(n):
    yield n
    for c in n.get('nodes',[]):yield from walk(c)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--allow-missing-media',action='store_true');ap.add_argument('--base',default='/fackeln-am-abgrund');a=ap.parse_args()
    pages={p:Page(p.read_text(encoding='utf-8')) for p in build.OUT.rglob('*.html')};errors=[];missing=set();text_nodes=0
    assert len(build.posts)==19, 'Expected 19 exported posts'
    assert len({p['slug'] for p in build.posts})==19
    for p in build.posts:
        path=build.OUT/'post'/p['slug']/'index.html';parsed=pages[path];nodes=[x for n in p['richContent']['nodes'] for x in walk(n)]
        actual=''.join(parsed.text)
        for n in nodes:
            if n['type']=='TEXT':
                text_nodes+=1
                if n['textData']['text'].replace('\n','') not in actual:errors.append('Missing text in '+p['slug'])
        assert parsed.tags['figure']==sum(n['type']=='IMAGE' for n in nodes),p['slug']
        assert parsed.tags['table']==sum(n['type']=='TABLE' for n in nodes),p['slug']
    for path,p in pages.items():
        assert p.tags['h1']==1,path
        for u in p.links:
            split=urlsplit(u)
            if split.scheme or split.netloc:continue
            relative=unquote(split.path)
            if relative.startswith(a.base+'/'):relative=relative[len(a.base)+1:]
            elif relative.startswith('/'):errors.append('Wrong base: '+u);continue
            if not relative:dest=build.OUT/'index.html' if split.path else path
            else:dest=build.OUT/relative
            if dest.is_dir():dest=dest/'index.html'
            if not dest.exists():
                if '/assets/' in u:missing.add(u)
                else:errors.append('Missing route '+u)
            elif split.fragment and dest in pages and unquote(split.fragment) not in pages[dest].ids:errors.append('Missing anchor '+u)
    if missing and not a.allow_missing_media:errors.append(f'{len(missing)} missing image files')
    report={'posts':19,'pages':len(pages),'text_nodes_checked':text_nodes,'missing_media':len(missing),'errors':errors}
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if errors:raise SystemExit(1)
if __name__=='__main__':main()
