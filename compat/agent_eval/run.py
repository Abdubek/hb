"""Run authenticated local models against the same frozen MCP preview tasks.

No implementation work is delegated. Models may only author scenes through hb
MCP in per-task Docker sandboxes. Preserve first attempts and provider failures.
"""
import argparse, concurrent.futures, hashlib, json, os, subprocess, sys, time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--image',required=True);p.add_argument('--limit',type=int,default=30);p.add_argument('--workers',type=int,default=4);p.add_argument('--provider',choices=['both','claude','gpt6'],default='both');a=p.parse_args()
root=Path(__file__).resolve().parents[2];out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
tasks=json.loads(Path(__file__).with_name('tasks.json').read_text())[:a.limit]
image_id=subprocess.check_output(['docker','image','inspect','--format','{{.Id}}',a.image],text=True).strip()
metadata={'image_id':image_id,'image_tag':a.image,'tasks_sha256':hashlib.sha256(Path(__file__).with_name('tasks.json').read_bytes()).hexdigest(),'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'proxy_sha256':hashlib.sha256(Path(__file__).with_name('proxy.py').read_bytes()).hexdigest(),'policy':'No source edits delegated; MCP-only modeling tasks in isolated containers; at most 15 run attempts; first three task families used in development pilot.'}
meta=out/'benchmark.json'
if meta.exists():
    if json.loads(meta.read_text())!=metadata:raise SystemExit('Benchmark inputs changed; use a fresh output directory.')
else:meta.write_text(json.dumps(metadata,indent=2)+'\n')

cli=root/'.build/eval-tools/node_modules/.bin';proxy=Path(__file__).with_name('proxy.py')

def run(provider,task):
    folder=out/provider/task['id']
    if (folder/'result.json').exists():return json.loads((folder/'result.json').read_text())
    folder.mkdir(parents=True,exist_ok=True);work=folder/'work';work.mkdir(exist_ok=True)
    if (folder/'prompt.txt').exists():raise RuntimeError(f'Preserved incomplete attempt at {folder}; use another output directory.')
    prompt=f'''Use only the hb MCP tools to build this scene in /session/scene.hb. This is an engine usability evaluation, not repository development. Do not use shell, file, web, delegation or other tools. First read hb_capabilities; consult hb_api when needed. You have at most 15 hb_run attempts. Use the code argument to submit scripts. Failed checks count as run attempts. Render, inspect the returned image, and use geometry queries to correct your result. Clear the scene explicitly if rebuilding. No assets, file reads, addons or external packages. Finish by calling hb_export with args ["/session/result.glb"] and hb_render with args ["--out","/session/preview.png","--views","iso","--size","512"]. Use a camera named Camera, aimed at the model, and at least two assigned materials. Required parts must have real nonempty mesh geometry; do not use invisible placeholders. Keep all required parts visible as an assembly.\n\nTask: {task['description']}.\nRequired exact mesh object names: {', '.join(task['required_meshes'])}.\nAcceptance: named nonempty parts, active Camera, at least two assigned materials, finite nondegenerate world bounds, requested dimensions/arrangement, successful GLB export and a preview image. This automatic structural score does not grade visual artistry. Stop after delivering or exhausting the attempt limit; report limitations honestly.'''
    (folder/'prompt.txt').write_text(prompt)
    args=[str(proxy),'--session',str(folder),'--image',image_id]
    if provider=='claude':
        config=folder/'mcp.json';config.write_text(json.dumps({'mcpServers':{'hb':{'command':sys.executable,'args':args}}}))
        cmd=[str(cli/'claude'),'-p','--model','claude-opus-5','--effort','medium','--tools','','--allowedTools','mcp__hb__*','--permission-mode','dontAsk','--strict-mcp-config','--mcp-config',str(config),'--setting-sources','','--no-session-persistence','--output-format','stream-json','--verbose','--max-budget-usd','3',prompt]
    else:
        cmd=[str(cli/'codex'),'exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','--sandbox','read-only','--disable','shell_tool','--json','--model','gpt-6-astra','-c','model_reasoning_effort="medium"','-c','mcp_servers.hb.command='+json.dumps(sys.executable),'-c','mcp_servers.hb.args='+json.dumps(args),'-c','mcp_servers.hb.default_tools_approval_mode="approve"','-c','mcp_servers.hb.startup_timeout_sec=45',prompt]
    begin=time.time();timed_out=False
    with (folder/'provider.jsonl').open('w') as output,(folder/'provider.stderr').open('w') as error:
        try:proc=subprocess.run(cmd,cwd=work,stdin=subprocess.DEVNULL,stdout=output,stderr=error,timeout=900);code=proc.returncode
        except subprocess.TimeoutExpired:code=None;timed_out=True
    result={'provider':provider,'model':'claude-opus-5' if provider=='claude' else 'gpt-6-astra','task':task['id'],'elapsed_seconds':time.time()-begin,'provider_exit':code,'timed_out':timed_out,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest()}
    (folder/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True);return result
providers=['claude','gpt6'] if a.provider=='both' else [a.provider]
with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
    jobs=[pool.submit(run,provider,task) for task in tasks for provider in providers]
    for future in concurrent.futures.as_completed(jobs):future.result()
