"""Run one new real-model Workflow with explicit presentation pauses."""
import asyncio, json, os, signal, sys, threading, time, uuid, subprocess
from datetime import timedelta
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
os.environ["GRPC_VERBOSITY"] = "ERROR"
from google.protobuf.json_format import MessageToDict

B = Path(__file__).resolve().parent
BASE = B
D = B / 'source'
R = Path(os.environ.get('KEYNOTE_CAPTURE_DIR', BASE / 'capture')).resolve()
R.mkdir(parents=True, exist_ok=False)
TARGET = os.environ.get('CADENCE_TARGET', 'localhost:7833')
DOMAIN = os.environ.get('CADENCE_DOMAIN', 'incident-demo')
WEB = os.environ.get('CADENCE_WEB_URL', 'http://localhost:8088').rstrip('/')
S = BASE / 'evidence' / ('run-' + uuid.uuid4().hex[:8])
S.mkdir(parents=True)
os.environ.update(INCIDENT_TRIAGE_MODEL='live', INCIDENT_TRIAGE_CATALOG=os.environ.get('INCIDENT_TRIAGE_CATALOG', str(D/'models.yaml')), INCIDENT_TRIAGE_STATE=str(S), INCIDENT_TRIAGE_CAPTURE_HOLDS='1')
sys.path.insert(0,str(D))
import cadence, story
from cadence.contrib.pydantic import PydanticDataConverter
from workflow import WORKFLOW, RecipeInput
from run_rehearsal import spawn_worker, stop_workers, history_events

W='keynote-'+uuid.uuid4().hex[:8]
processes=[]
off=False
last={}
terminal=[]
def term(value):
    terminal.append(value)
    write('terminal.json',{'lines':terminal})
def command(args):
    term('$ '+ ' '.join(args))
    result=subprocess.run(args,capture_output=True,text=True)
    term(result.stdout.strip() or ('(no matching processes)' if result.returncode == 1 and args[0] == 'ps' else result.stderr.strip() or '(command completed)'))
    return result
def terminal_workers(label):
    term(label)
    command(['ps','-p',','.join(str(p.pid) for p in processes),'-o','pid=,stat=,ucomm='])
def terminal_kill():
    pids=[str(p.pid) for p in processes]
    command(['kill','-KILL',*pids])
    for p in processes:p.wait(timeout=10)
    command(['ps','-p',','.join(pids),'-o','pid=,stat=,ucomm='])
    term('Owned demo Workers alive: 0')


def rows(path):
    try: return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    except FileNotFoundError: return []

def usage():
    values=rows(S/'model-spend.jsonl')
    return {'calls':len(values),'input_tokens':sum(x['input_tokens'] for x in values),'output_tokens':sum(x['output_tokens'] for x in values)}

def write(name,obj):
    target=R/name
    temp=target.with_suffix('.tmp')
    temp.write_text(json.dumps(obj,indent=2))
    temp.replace(target)

def workers(suffix):
    for role,name in [('workflow','workflow-'+suffix),('activity','activities-'+suffix)]:
        processes.append(spawn_worker(role,name,W,TARGET,DOMAIN,S))

class Handler(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

async def run():
    global off,last
    server=ThreadingHTTPServer(('127.0.0.1',28220),partial(Handler,directory=str(R)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    c=cadence.Client(domain=DOMAIN,target=TARGET,identity='chronological-capture',data_converter=PydanticDataConverter())
    try:
        workers('A')
        terminal_workers('Initial Workers')
        await asyncio.sleep(1)
        (S/'faults.json').write_text(json.dumps({W:{'logs':{'status':429,'times':1}}}))
        ex=await c.start_workflow(WORKFLOW,RecipeInput(text=story.trace_text(),limits={'scan_seconds':.4,'rescan_seconds':.2,'approval_window_seconds':86400,'presentation_mode':True,'inject_duplicate':True,'repeat_limit':1}),task_list=W,workflow_id=W,execution_start_to_close_timeout=timedelta(hours=2),task_start_to_close_timeout=timedelta(seconds=30))
        manifest={'workflow_id':W,'run_id':ex.run_id,'url':f'{WEB}/domains/{DOMAIN}/workflows/{W}/{ex.run_id}/history','state_dir':str(S),'scope':'fresh live Qwen; synthetic incident/logs/tools; explicit 429, injected duplicate and Worker-loss tests; real presentation waits','start':time.time(),'presentation_holds':'Workflow gates and heartbeat-protected pending log Activities, released by recorder'}
        write('manifest.json',manifest)
        print(json.dumps(manifest),flush=True)
        while True:
            action=R/'control.json'
            if action.exists():
                v=json.loads(action.read_text());action.unlink()
                if v['action']=='release':
                    await c.signal_workflow(W,'','presentation_continue',v['checkpoint'])
                elif v['action']=='release_activity':
                    (S/'activity-gates'/v['token']).touch()
                elif v['action']=='stop_workers':
                    terminal_kill();processes.clear();off=True
                    events=await history_events(c,W,ex.run_id)
                    write('owned-workers-stopped.json',{'at':time.time(),'pids_alive':[],'history_events':len(events),'usage':usage(),'run_id':ex.run_id})
                    term('Run remains open. Cadence and its database are running.')
                    term('Model responses before stop: '+str(usage()['calls']))
                    print('OWNED WORKERS STOPPED',flush=True)
                elif v['action']=='restart_workers':
                    workers('B');off=False
                    terminal_workers('Replacement Workers')
                    write('owned-workers-restarted.json',{'at':time.time(),'pids':[p.pid for p in processes],'usage':usage(),'run_id':ex.run_id})
                elif v['action']=='finish': break
            if not off:
                try: last=await asyncio.wait_for(c.query_workflow(W,'','status',result_type=dict),timeout=4)
                except Exception as e: print('QUERY',type(e).__name__,flush=True)
            events=await history_events(c,W,ex.run_id)
            history=[MessageToDict(e,preserving_proto_field_name=True) for e in events]
            write('live-history.json',history)
            waiting=[]
            for gate in (S/'activity-gates').glob('*.waiting.json'):
                item=json.loads(gate.read_text())
                if not (gate.parent/item['token']).exists():waiting.append(item)
            ledger=rows(S/'ledger.jsonl')
            write('status.json',{'at':time.time(),'state':last,'workers_running':not off,'worker_pids':[p.pid for p in processes],'usage':usage(),'ledger':ledger,'waiting_activities':waiting,'history_events':len(history),**manifest})
            if last.get('phase')=='DONE':
                await asyncio.sleep(1)
                events=await history_events(c,W,ex.run_id)
                write('final-history.json',[MessageToDict(e,preserving_proto_field_name=True) for e in events])
                term('Workflow phase: DONE')
                term('Server completion event: '+str(any(e.HasField('workflow_execution_completed_event_attributes') for e in events)))
                term('Model responses after recovery: '+str(usage()['calls']))
                write('result.json',{'state':last,'usage':usage(),'ledger':ledger,'history_events':len(events),'service_completed':any(e.HasField('workflow_execution_completed_event_attributes') for e in events),**manifest})
                print('DONE',flush=True)
                while not (R/'recording-finished').exists():
                    await asyncio.sleep(.3)
                break
            await asyncio.sleep(.3)
    finally:
        stop_workers(processes)
        await c.close()
        server.shutdown()

asyncio.run(run())
