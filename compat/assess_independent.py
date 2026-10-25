"""Run unchanged independent sources in an externally isolated container.

Mount project read-only, disable network, bound CPU/RAM, and expose only a dedicated
results directory writable. This is corpus compatibility, not the held-out MCP eval.
"""
import argparse,hashlib,json,subprocess,time,tempfile
from pathlib import Path
from independent_semantics import compare
p=argparse.ArgumentParser();p.add_argument('--hb',required=True);p.add_argument('--blender',required=True);p.add_argument('--out',required=True);p.add_argument('--timeout',type=int,default=120);a=p.parse_args()
root=Path(__file__).resolve().parents[1];out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
hb=Path(a.hb).resolve();engine_hash=hashlib.sha256(hb.read_bytes()).hexdigest()
runner_hash=hashlib.sha256(b''.join((root/'compat'/name).read_bytes() for name in ('assess_independent.py','independent_reference.py','independent_semantics.py'))).hexdigest()
def run(command,folder,tag):
    start=time.monotonic()
    with (folder/(tag+'.stdout')).open('w') as stdout,(folder/(tag+'.stderr')).open('w') as stderr:
        try:r=subprocess.run(command,cwd=folder,stdout=stdout,stderr=stderr,timeout=a.timeout);code=r.returncode
        except subprocess.TimeoutExpired:code='timeout'
    return {'returncode':code,'elapsed_seconds':time.monotonic()-start}
rows=[]
for source in sorted((root/'compat/independent').glob('*.py')):
    folder=out/source.stem;folder.mkdir(exist_ok=True);record=folder/'record.json';source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    if record.exists():
        prior=json.loads(record.read_text())
        if prior['engine_sha256']==engine_hash and prior['source_sha256']==source_hash and prior.get('runner_sha256')==runner_hash:rows.append(prior);continue
    folder=Path(tempfile.mkdtemp(prefix='attempt-',dir=folder))
    row={'file':str(source.relative_to(root)),'source_sha256':source_hash,'engine_sha256':engine_hash,'runner_sha256':runner_hash,'artifacts':str(folder.relative_to(out))}
    row['check']=run([str(hb),'check',str(source)],folder,'check')
    row['blender_process']=run([a.blender,'-b','--factory-startup','--python-exit-code','1','--python',str(root/'compat/independent_reference.py'),'--',str(source),str(folder/'blender.json'),str(folder/'blender.glb')],folder,'blender')
    row['blender']=json.loads((folder/'blender.json').read_text()) if (folder/'blender.json').exists() else {'ok':False,'phase':'process','error':str(row['blender_process']['returncode'])}
    row['hb']=run([str(hb),'run',str(source),'--scene',str(folder/'scene.hb'),'--out',str(folder/'hb.glb')],folder,'hb')
    row['static_pass']=row['check']['returncode']==0;row['runtime_pass']=row['hb']['returncode']==0
    row['blender_pass']=row['blender'].get('ok',False);row['compatible_execution']=row['blender_pass'] and row['runtime_pass']
    if row['compatible_execution']:
        try:row['semantics']=compare(folder/'blender.glb',folder/'hb.glb')
        except (AssertionError,KeyError,ValueError,TypeError,IndexError) as exc:row['semantics']={'passed':False,'error':str(exc)}
    row['semantic_pass']=row.get('semantics',{}).get('passed',False)
    record.write_text(json.dumps(row,indent=2)+'\n');rows.append(row)
    print(json.dumps({'file':source.name,'blender':row['blender_pass'],'static':row['static_pass'],'runtime':row['runtime_pass'],'semantics':row['semantic_pass']}),flush=True)
report={'kind':'independent unmodified sources; execution and named GLB structure/material/transform/count/bounds checks; no pixel or full-topology equivalence claim','engine_sha256':engine_hash,'runner_sha256':runner_hash,'scripts':len(rows),'blender_pass':sum(r['blender_pass'] for r in rows),'static_pass':sum(r['static_pass'] for r in rows),'runtime_pass':sum(r['runtime_pass'] for r in rows),'compatible_execution':sum(r['compatible_execution'] for r in rows),'semantic_pass':sum(r['semantic_pass'] for r in rows),'static_accepted_runtime_failed':[r['file'] for r in rows if r['static_pass'] and not r['runtime_pass']],'rows':rows}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='rows'}))
