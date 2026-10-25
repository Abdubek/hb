"""Supplemental cohort only; never changes the original corpus or its scorer."""
import argparse,hashlib,json,subprocess,time
from pathlib import Path
from independent_semantics import compare
p=argparse.ArgumentParser();p.add_argument('--hb',required=True);p.add_argument('--blender',required=True);p.add_argument('--out',required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1];out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=False);hb=Path(a.hb).resolve();cohort=json.loads(Path(__file__).with_name('github').joinpath('provenance.json').read_text());rows=[]
def run(command,folder,tag):
    start=time.monotonic()
    with (folder/(tag+'.stdout')).open('w') as stdout,(folder/(tag+'.stderr')).open('w') as stderr:
        try:r=subprocess.run(command,cwd=folder,stdout=stdout,stderr=stderr,timeout=60);code=r.returncode
        except subprocess.TimeoutExpired:code='timeout'
    return {'returncode':code,'seconds':time.monotonic()-start}
for repo in cohort['repositories']:
    for file in repo['sources']:
        source=root/repo['local_directory']/file['path'];assert hashlib.sha256(source.read_bytes()).hexdigest()==file['sha256']
        folder=out/(repo['repository'].split('/')[0]+'-'+file['path'].replace('/','_'));folder.mkdir()
        row={'repository':repo['repository'],'file':file['path'],'sha256':file['sha256']}
        row['check']=run([str(hb),'check',str(source)],folder,'check')
        row['hb']=run([str(hb),'run',str(source),'--scene',str(folder/'scene.hb'),'--out',str(folder/'hb.glb')],folder,'hb')
        row['blender_process']=run([a.blender,'-b','--factory-startup','-t','1','--python-exit-code','1','--python',str(root/'compat/github_reference.py'),'--',str(source),str(folder/'blender.json'),str(folder/'blender.glb')],folder,'blender')
        row['blender']=json.loads((folder/'blender.json').read_text()) if (folder/'blender.json').exists() else {'ok':False,'error':str(row['blender_process']['returncode'])}
        row['static_pass']=row['check']['returncode']==0;row['runtime_pass']=row['hb']['returncode']==0;row['blender_pass']=row['blender'].get('ok',False);row['semantic_pass']=False
        if row['runtime_pass'] and row['blender_pass']:
            try:row['semantics']=compare(folder/'blender.glb',folder/'hb.glb');row['semantic_pass']=row['semantics']['passed']
            except (AssertionError,KeyError,ValueError,TypeError,IndexError) as e:row['semantics']={'passed':False,'error':str(e)}
        (folder/'record.json').write_text(json.dumps(row,indent=2)+'\n');rows.append(row);print(json.dumps({k:v for k,v in row.items() if k in ['file','static_pass','runtime_pass','blender_pass','semantic_pass']}),flush=True)
report={'engine_sha256':hashlib.sha256(hb.read_bytes()).hexdigest(),'scripts':len(rows),'rows':rows,'method':'Preserved full scripts, no edits or automatic ports; Blender factory startup and source-directory imports; hb empty scene and its documented import policy; 60-second per-process cap, no network, repository read-only. Separate cohort, original 200 unchanged.'}
for k in ['static_pass','runtime_pass','blender_pass','semantic_pass']:report[k]=sum(r[k] for r in rows)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
