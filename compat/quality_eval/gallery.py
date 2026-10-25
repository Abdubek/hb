"""Build a blind, self-contained pairwise visual rating page from real artifacts.

Input: {"pairs": [{"id": "...", "brief": "...", "a": {"label": "baseline",
"image": "path.png", "seconds": 1.2}, "b": {...}}]}. Paths are relative to
input JSON. Identity mapping stays in a separate key.json, not in the HTML.
This tool never invents model outcomes, scores, images or timing measurements.
"""
import argparse
import base64
import hashlib
import html
import json
from pathlib import Path
import random


def build(source, out, seed):
    source=Path(source).resolve();out=Path(out).resolve()
    if out.exists():raise ValueError('Use a fresh output directory; preserve previous ratings.')
    data=json.loads(source.read_text());rng=random.Random(seed);panels=[];key=[]
    if not data['pairs']:raise ValueError('At least one comparison pair is required')
    seen=set()
    for pair in data['pairs']:
        if pair['id'] in seen:raise ValueError('Duplicate pair id')
        seen.add(pair['id']);variants=[pair['a'],pair['b']]
        if variants[0]['label']==variants[1]['label']:raise ValueError('Use distinct variant labels in each pair')
        rng.shuffle(variants)
        images=[];identities=[]
        for index,variant in enumerate(variants):
            image=(source.parent/variant['image']).read_bytes()
            if not image.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('Each compared artifact must be PNG')
            digest=hashlib.sha256(image).hexdigest()
            images.append('<figure><figcaption>'+('A','B')[index]+'</figcaption><img src="data:image/png;base64,'+base64.b64encode(image).decode()+'"></figure>')
            identities.append({**variant,'image_sha256':digest})
        idx=len(key)
        key.append({'id':pair['id'],'sides':identities})
        rubric=''.join('<li>'+html.escape(x)+'</li>' for x in pair.get('rubric',[]))
        panels.append('<section data-id="'+html.escape(pair['id'],quote=True)+'"><h2>'+html.escape(pair['id'])+'</h2><p>'+html.escape(pair['brief'])+'</p><ul>'+rubric+'</ul><div class="pair">'+''.join(images)+'</div><label>Preferred result <select required><option value="">Choose after viewing</option><option>A</option><option>B</option><option>Tie</option><option>Neither</option></select></label><label>Reason <textarea required placeholder="Brief, silhouette, materials, composition, defects"></textarea></label></section>')
    out.mkdir(parents=True)
    keydata={'format':'hb-blind-pairs-v1','seed':seed,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'pairs':key}
    keydata['presentation_id']=hashlib.sha256(json.dumps(key,sort_keys=True).encode()).hexdigest()
    (out/'key.json').write_text(json.dumps(keydata,indent=2)+'\n')
    document='''<!doctype html><html lang="en"><meta charset="utf-8"><title>Visual pair review</title><style>
body{font:16px system-ui;background:#15191e;color:#e9eef4;max-width:1200px;margin:40px auto;padding:0 24px}p,li{line-height:1.5;color:#c3cdd8}section{margin:36px 0;padding:24px;background:#202731;border-radius:12px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0}img{width:100%;background:#111}figcaption{font-size:24px;padding:8px}label{display:block;margin-top:16px}textarea{display:block;width:95%;min-height:72px}select,textarea,button{font:inherit;padding:10px;border-radius:6px}button{cursor:pointer}header{position:sticky;top:0;background:#15191e;padding:12px 0}@media(max-width:650px){.pair{grid-template-columns:1fr}}
</style><header><h1>Which result better answers the brief?</h1><button id="save">Download ratings</button><span id="status"></span></header><p>Compare the images at equal size. Tie and Neither are valid answers. This page does not reveal provider or engine labels and does not assign automatic artistic scores.</p>'''+''.join(panels)+'''<script>
const sections=[...document.querySelectorAll('section')];
const storage='hb-pair-review:'+''' + json.dumps(keydata['presentation_id']) + ''';
try{const saved=JSON.parse(localStorage.getItem(storage)||'[]');sections.forEach((s,i)=>{if(saved[i]){s.querySelector('select').value=saved[i].preference;s.querySelector('textarea').value=saved[i].reason}})}catch{}
function ratings(){return sections.map(s=>({id:s.dataset.id,preference:s.querySelector('select').value,reason:s.querySelector('textarea').value.trim()}))}
document.addEventListener('input',()=>{try{localStorage.setItem(storage,JSON.stringify(ratings()))}catch{}});
document.querySelector('#save').onclick=()=>{const r=ratings();if(r.some(x=>!x.preference||!x.reason)){document.querySelector('#status').textContent=' Complete each preference and reason.';return}const blob=new Blob([JSON.stringify({format:'hb-blind-ratings-v1',presentation_id:storage.split(':')[1],ratings:r},null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='ratings.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)};
</script></html>'''
    (out/'index.html').write_text(document)
    return keydata


def score(key, ratings):
    k=json.loads(Path(key).read_text());r=json.loads(Path(ratings).read_text())
    if r.get('presentation_id')!=k['presentation_id']:raise ValueError('Ratings belong to a different image/side assignment')
    rows=r['ratings'];byid={x['id']:x for x in rows}
    if len(rows)!=len(byid) or set(byid)!={x['id'] for x in k['pairs']}:raise ValueError('Require exactly one rating for every pair')
    tally={};details=[]
    for pair in k['pairs']:
        row=byid[pair['id']];preference=row['preference']
        if preference not in ('A','B','Tie','Neither') or not row['reason'].strip():raise ValueError('Invalid or incomplete rating')
        for variant in pair['sides']:tally.setdefault(variant['label'],{'wins':0,'losses':0,'ties':0,'neither':0})
        for i,variant in enumerate(pair['sides']):
            field='ties' if preference=='Tie' else 'neither' if preference=='Neither' else 'wins' if preference==('A','B')[i] else 'losses'
            tally[variant['label']][field]+=1
        details.append({**pair,'rating':row})
    return {'kind':'Human pairwise preferences; no automatic aesthetic score or statistical superiority claim','tally':tally,'pairs':details}

if __name__=='__main__':
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
    b=sub.add_parser('build');b.add_argument('source');b.add_argument('--out',required=True);b.add_argument('--seed',type=int,default=719)
    s=sub.add_parser('score');s.add_argument('--key',required=True);s.add_argument('--ratings',required=True)
    a=p.parse_args()
    print(json.dumps(build(a.source,a.out,a.seed) if a.command=='build' else score(a.key,a.ratings),indent=2))
