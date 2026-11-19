#!/usr/bin/env python3
"""Check generated page metadata, routes, assets, anchors and approved assets."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import json
root=Path(__file__).resolve().parent;dist=root/'dist'
class Page(HTMLParser):
 def __init__(self,text):
  super().__init__();self.links=[];self.ids=set();self.h1=0;self.meta={};self.lang=None;self.alternates=[];self.feed(text)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='html':self.lang=a.get('lang')
  if tag=='h1':self.h1+=1
  if 'id' in a: assert a['id'] not in self.ids;self.ids.add(a['id'])
  if tag in ['a','link','script','img','image']:
   u=a.get('href',a.get('src',''))
   if u:self.links.append(u)
  if tag=='meta':self.meta[a.get('name',a.get('property'))]=a.get('content')
  if tag=='link' and a.get('rel')=='alternate':self.alternates.append(a.get('hreflang'))
pages={p:Page(p.read_text()) for p in dist.rglob('*.html')}
for p,doc in pages.items():
 if 'legacy' in p.relative_to(dist).parts or p.name=='privacy.html':continue
 assert doc.lang in ['en','fr'],p
 assert doc.h1==1,p
 assert doc.meta.get('description'),p
 assert set(doc.alternates)=={'en','fr','x-default'},p
 for u in doc.links:
  v=urlsplit(u)
  if v.scheme or v.netloc:continue
  target=dist/v.path.lstrip('/') if v.path else p
  if target.is_dir():target=target/'index.html'
  assert target.exists(),(p,u)
  if v.fragment and target in pages:assert v.fragment in pages[target].ids,(p,u)
 for txt in ['Phoenix','niororesources@gmail.com','HR43ZR93H2Z1']:
  assert txt not in p.read_text(),(p,txt)
for name in ['logo-primary.png','logo-reversed.png','logo-icon.png']:
 assert (dist/'assets'/name).read_bytes()==(root/'src/assets'/name).read_bytes()
for lang in ['en','fr']:
 text=(dist/lang/'index.html').read_text();assert 'US / AF / EU / AS' in text
assert len(list((dist/'en').rglob('index.html')))==16
assert len(list((dist/'fr').rglob('index.html')))==16
print(f'PASS: {len(pages)} pages; internal routes, anchors, assets, metadata and bilingual map labels.')

for lang in ['en','fr']:
 page=(dist/lang/'global-network/index.html').read_text()
 for country in ['us','sn','fr','it','tr','cn']:
  assert 'data-map-country="'+country+'"' in page
  assert 'data-country-panel="'+country+'"' in page
 for slug,category in [('sourcing',7),('furniture',8),('applications',9)]:
  assert '?category='+str(category)+'#inquiry' in (dist/lang/('solutions/'+slug+'/index.html')).read_text()
print('PASS: six country controls and panels; all new solution inquiry categories.')
