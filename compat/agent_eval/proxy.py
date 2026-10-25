"""Evaluation-only MCP recorder: hb runs in an isolated, networkless container.

The proxy forwards actual hb MCP responses, including images. It caps run calls
at 15; it does not implement or replace hb tools. No repository mount is exposed.
"""
import argparse, json, subprocess, sys, threading, time, hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--session',required=True);p.add_argument('--image',required=True);a=p.parse_args()
root=Path(a.session).resolve();assets=root/'artifacts';assets.mkdir(exist_ok=True)
log=(root/'mcp.jsonl').open('a',buffering=1);lock=threading.Lock()
def record(kind,value):
    if kind=='response' and isinstance(value.get('result'),dict):
        value=json.loads(json.dumps(value))
        for item in value['result'].get('content',[]):
            if item.get('type')=='image':
                data=item.pop('data');item['recorded_base64_sha256']=hashlib.sha256(data.encode()).hexdigest()
    with lock:log.write(json.dumps({'time':time.time(),'kind':kind,'message':value})+'\n')
command=['docker','run','--rm','-i','--platform','linux/amd64','--pull','never','--network','none','--read-only','--tmpfs','/tmp:rw,size=128m','--memory','512m','--cpus','1','--pids-limit','64','-v',str(assets)+':/session:rw','-w','/session',a.image,'serve','--mcp']
with (root/'engine.stderr').open('w') as error:
    process=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=error,text=True,bufsize=1)
    def receive():
        for line in process.stdout:
            try:record('response',json.loads(line))
            except json.JSONDecodeError:pass
            with lock:sys.stdout.write(line);sys.stdout.flush()
    reader=threading.Thread(target=receive,daemon=True);reader.start();runs=0;calls=0
    try:
        for line in sys.stdin:
            request=json.loads(line);record('request',request)
            if request.get('method')=='tools/call':
                calls+=1
                if request.get('params',{}).get('name')=='hb_run':runs+=1
                if runs>15 or calls>100:
                    response={'jsonrpc':'2.0','id':request.get('id'),'result':{'isError':True,'content':[{'type':'text','text':'Evaluation limit reached: at most 15 run attempts and 100 tool calls.'}]}}
                    record('response',response)
                    with lock:print(json.dumps(response),flush=True)
                    continue
            process.stdin.write(line);process.stdin.flush()
    finally:
        process.stdin.close();reader.join(timeout=5)
        if process.poll() is None:process.terminate()
