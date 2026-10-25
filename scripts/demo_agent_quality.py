"""Reproducible product scene and blind draft/final renderer comparison.

This is authored demonstration code, not an autonomous-agent benchmark. It creates
review receipts but deliberately does not fabricate a visual assessment/delivery.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

p=argparse.ArgumentParser();p.add_argument('--hb',default='target/release/hb');p.add_argument('--out',required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1];hb=Path(a.hb).resolve();out=Path(a.out).resolve()
if out.exists():raise SystemExit('Use a fresh output directory to retain prior results.')
out.mkdir(parents=True)
scene=out/'product.hb';calls=[]
def call(*args):
    r=subprocess.run([str(hb),*map(str,args)],capture_output=True,text=True,cwd=out)
    record={'args':list(map(str,args)),'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr};calls.append(record)
    (out/'calls.json').write_text(json.dumps(calls,indent=2)+'\n')
    if r.returncode:raise RuntimeError(r.stdout+r.stderr)
    return json.loads(r.stdout)
def recipe(name,params):return call('recipe',name,'--params',json.dumps(params))['code']
code=recipe('housing',{'dimensions':[2.4,1.5,.35],'location':[0,0,.175],'bevel':.08})
code+='\n'+recipe('cable',{'points':[[1.2,-.25,.15],[1.65,-.25,.16],[1.7,-1.,.12],[2.3,-.9,.1]],'radius':.045,'color':[.7,.18,.025]})
code+='\n'+recipe('label',{'font':str(root/'compat/fixtures/fonts/DejaVuSans.ttf'),'text':'HB','size':.55,'extrude':.008,'location':[.65,.13,.36]})
code+='''
import bpy
for i,(x,y) in enumerate([(-.72,-.3),(-.25,-.3),(-.72,.3),(-.25,.3)]):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.14,depth=.075,location=(x,y,.38))
    obj=bpy.context.object;obj.name='Button '+str(i+1)
    mat=bpy.data.materials.new('Button surface '+str(i+1));mat.diffuse_color=(.055,.065,.08,1);mat.roughness=.4
    obj.data.materials.append(mat)
    for f in obj.data.polygons:f.use_smooth=len(f.vertices)==4
    bevel=obj.modifiers.new('Button rim','BEVEL');bevel.width=.018;bevel.segments=4
bpy.ops.mesh.primitive_plane_add(size=12)
obj=bpy.context.object;obj.name='Backdrop';obj.location.z=-.018
mat=bpy.data.materials.new('Backdrop');mat.diffuse_color=(.055,.065,.08,1);mat.roughness=.8;obj.data.materials.append(mat)
'''
code+='\n'+recipe('studio',{'target':[.45,-.15,.25],'span':3.4})
script=out/'product.py';script.write_text(code)
call('check',script);run=call('run',script,'--scene',scene)
measurements={}
for quality in ('draft','final'):
    measurements[quality]=call('render','--scene',scene,'--views','camera','--size',512,'--quality',quality,'--out',out/(quality+'.png'))
review=call('review','--scene',scene,'--size',512,'--out',out/'review.json')
call('export',out/'product.glb','--scene',scene)
pairs={'pairs':[{'id':'product-preview','brief':'Compare edge smoothness, controlled highlights and shadow artifacts on the same product geometry. This is a renderer-only comparison.','a':{'label':'draft','image':'draft.png','seconds':measurements['draft']['total_ms']/1000},'b':{'label':'final','image':'final.png','seconds':measurements['final']['total_ms']/1000}}]}
(out/'pairs.json').write_text(json.dumps(pairs,indent=2)+'\n')
subprocess.run([sys.executable,str(root/'compat/quality_eval/gallery.py'),'build',str(out/'pairs.json'),'--out',str(out/'blind')],check=True,stdout=subprocess.DEVNULL)
report={'kind':'Authored demo; no agent or preference score','binary_sha256':hashlib.sha256(hb.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),'revision':run['revision'],'render':measurements,'diagnostics':review['review']['diagnostics']}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'output':str(out),'revision':run['revision'],'errors':report['diagnostics']['errors'],'warnings':report['diagnostics']['warnings']}))
