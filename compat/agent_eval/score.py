"""Score preserved MCP outcomes. No model self-reported success is trusted.

Structural/transport score only: named meshes, materials, camera, bounds, task
relations, saved export/preview and actual successful MCP calls. No visual-quality
or Blender-parity claim. Retain task-level reasons, attempts and first-run status.
"""
import argparse, hashlib, json, math, statistics, struct, subprocess, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from normalize import revision
p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--hb',required=True);a=p.parse_args()
root=Path(a.out).resolve();hb=str(Path(a.hb).resolve());tasks=json.loads(Path(__file__).with_name('tasks.json').read_text());results=[]
for provider in ['claude','gpt6']:
 for task in tasks:
    folder=root/provider/task['id']
    if not (folder/'result.json').exists():continue
    row=json.loads((folder/'result.json').read_text());fail=[];runs=0;errors=0;unsupported=0;successful_runs=0;rendered=False;exported=False;queried=False;first_run=False;requests={}
    for line in (folder/'mcp.jsonl').read_text().splitlines() if (folder/'mcp.jsonl').exists() else []:
        event=json.loads(line);m=event['message']
        if event['kind']=='request':
            if m.get('method')=='tools/call':
                name=m.get('params',{}).get('name');requests[m.get('id')]=name
                if name=='hb_run':runs+=1
        elif m.get('id') in requests:
            name=requests[m['id']];v=m.get('result',{});data=v.get('structuredContent',{});ok=v.get('isError') is False and data.get('ok',True)
            if v.get('isError') or 'error' in m:
                errors+=1
                text=json.dumps(data)
                if 'UNSUPPORTED' in text:unsupported+=1
            if name=='hb_run' and ok:successful_runs+=1;first_run=first_run or runs==1
            rendered|=name=='hb_render' and ok;exported|=name=='hb_export' and ok;queried|=name=='hb_query' and ok
    cost=0;usage=[];non_mcp=[];provider_errors=[]
    for line in (folder/'provider.jsonl').read_text().splitlines():
        event=json.loads(line)
        if provider=='claude':
            if event.get('type')=='result':
                cost+=event.get('total_cost_usd',0)
                usage.append(event.get('usage',{}))
                if event.get('is_error'):provider_errors.append(event.get('subtype','provider error'))
            for block in event.get('message',{}).get('content',[]):
                if isinstance(block,dict) and block.get('type')=='tool_use' and not block.get('name','').startswith('mcp__hb__hb_'):non_mcp.append(block.get('name'))
        else:
            item=event.get('item',{})
            if item.get('type')=='mcp_tool_call' and item.get('server')!='hb':non_mcp.append(item.get('server'))
            if item.get('type') in ('command_execution','file_change','web_search','collab_tool_call'):non_mcp.append(item['type'])
            if event.get('type')=='turn.completed':usage.append(event.get('usage',{}))
            if event.get('type') in ('turn.failed','error'):provider_errors.append(event.get('message',event.get('error')))
    if non_mcp:fail.append('non-hb tool use: '+str(non_mcp))
    if provider_errors:fail.append('provider reported error: '+str(provider_errors))
    row.update(reported_cost_usd=cost if provider=='claude' else None,usage=usage,non_hb_tools=non_mcp)
    if row['provider_exit']!=0:fail.append('provider failed or timed out')
    if not 1<=runs<=15:fail.append('run attempt count outside 1..15')
    if not rendered or not exported or not queried:fail.append('missing successful MCP render/export/query')
    assets=folder/'artifacts';scene=assets/'scene.hb';bounds={}
    try:
        s=revision(scene)['scene'];objects={o['name']:o for o in s['objects']};meshes={m['id']:m for m in s['meshes']}
        for name in task['required_meshes']:
            o=objects.get(name);m=meshes.get((o.get('data') or {}).get('id')) if o and (o.get('data') or {}).get('kind')=='meshes' else None
            if not m or not m['vertices'] or not m['faces']:fail.append('missing nonempty mesh: '+name)
        camera=objects.get(task['camera'])
        if not camera or (camera.get('data') or {}).get('kind')!='cameras' or s.get('camera')!=camera['id']:fail.append('missing active named camera')
        used=set()
        for mesh in s['meshes']:
            for face_index in mesh.get('material_indices',[]):
                if 0<=face_index<len(mesh['materials']):used.add(mesh['materials'][face_index])
        if len(used)<task['minimum_materials']:fail.append('fewer than two materials assigned to faces')
        q=subprocess.run([hb,'query','bbox','--all','--scene',str(scene)],capture_output=True,text=True,timeout=30);data=json.loads(q.stdout)
        if not data.get('ok'):raise ValueError(data)
        bounds={v['name']:v['bbox'] for v in data['result']['objects']}
        visible=subprocess.run([hb,'query','visible','--camera',task['camera'],'--scene',str(scene)],capture_output=True,text=True,timeout=30)
        view=json.loads(visible.stdout)
        if not view.get('ok') or not set(task['required_meshes'])<=set(view.get('result',{}).get('objects',[])):fail.append('required parts outside the named camera frustum')

        for name in task['required_meshes']:
            b=bounds.get(name)
            if not b or not all(math.isfinite(v) for k in ['min','max','dimensions'] for v in b[k]) or sum(d>1e-5 for d in b['dimensions'])<2:fail.append('invalid/degenerate evaluated bounds: '+name)
        if task['special'].get('floor_xy') and any(abs(x-y)>1e-4 for x,y in zip(bounds['Floor']['dimensions'][:2],task['special']['floor_xy'])):fail.append('floor dimensions differ from 4x5 meters')
        if task['id']=='02-rover':
            left=[bounds['Wheel L'+str(i)]['center'] for i in range(1,4)];right=[bounds['Wheel R'+str(i)]['center'] for i in range(1,4)]
            if not any(max(x[axis] for x in left)<min(x[axis] for x in right)-1e-4 or max(x[axis] for x in right)<min(x[axis] for x in left)-1e-4 for axis in [0,1]):fail.append('wheel groups not on opposite sides')
            if len({tuple(v) for v in left+right})!=6:fail.append('wheel centers overlap')
        if task['id']=='20-stairs' and not all(bounds[f'Step {i}']['max'][2]<bounds[f'Step {i+1}']['max'][2]-1e-4 for i in range(1,5)):fail.append('steps are not progressively taller')
        data=(assets/'result.glb').read_bytes();length=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+length]);names={n['name'] for n in doc['nodes'] if 'mesh' in n}
        if not set(task['required_meshes'])<=names:fail.append('required geometry absent from export')
        png=(assets/'preview.png').read_bytes()
        if png[:8]!=b'\x89PNG\r\n\x1a\n' or struct.unpack('>II',png[16:24])!=(512,512):fail.append('missing 512px preview')
    except Exception as e:fail.append('artifact inspection: '+str(e))
    row.update(structural_pass=not fail,failures=fail,run_attempts=runs,successful_runs=successful_runs,first_run_executed=first_run,tool_errors=errors,unsupported_responses=unsupported,review_image=str((assets/'preview.png').relative_to(root)))
    results.append(row)
summary={'kind':'constrained preview MCP workflow benchmark; structural acceptance, not visual-quality or unrestricted Blender compatibility','scorer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'tasks_sha256':hashlib.sha256(Path(__file__).with_name('tasks.json').read_bytes()).hexdigest(),'scoring_binary_sha256':hashlib.sha256(Path(hb).read_bytes()).hexdigest(),'results':results,'providers':{}}
for provider in ['claude','gpt6']:
    rows=[r for r in results if r['provider']==provider]
    if rows:summary['providers'][provider]={'completed':len(rows),'structural_pass':sum(r['structural_pass'] for r in rows),'first_run_executed':sum(r['first_run_executed'] for r in rows),'total_run_attempts':sum(r['run_attempts'] for r in rows),'tool_errors':sum(r['tool_errors'] for r in rows),'unsupported_responses':sum(r['unsupported_responses'] for r in rows),'median_run_attempts':statistics.median(r['run_attempts'] for r in rows),'median_elapsed_seconds':statistics.median(r['elapsed_seconds'] for r in rows)}
(root/'report.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary['providers'],indent=2))
