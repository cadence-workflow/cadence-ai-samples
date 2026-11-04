"""Measure uncheckpointed restarts against the exact recorded Cadence Run."""
from pathlib import Path
import json, hashlib, sqlite3, collections
from measurement_helpers import capture_raw, metrics, usage, request_equivalence, read, save
B=Path(__file__).resolve().parent
C=Path(__import__('os').environ.get('KEYNOTE_CAPTURE_DIR', B.parent/'capture'))
run=json.loads((C/'result.json').read_text())
assert run['service_completed'] and run['state']['phase']=='DONE'
state=Path(run['state_dir'])
root=B/'measured';root.mkdir(exist_ok=False)
raw=capture_raw(root)
cad=metrics(state);rawcounts=metrics(root/'raw')
before=json.loads((C/'owned-workers-stopped.json').read_text());after=json.loads((C/'owned-workers-restarted.json').read_text())
assert before['usage']==after['usage']==run['usage']==usage(state)
assert before['pids_alive']==[]
assert before['run_id']==after['run_id']==run['run_id']
cad['recovery_calls']=0;rawcounts['recovery_calls']=raw['recovery_calls']
eq=request_equivalence(state,root/'raw')
result={'scope':'The exact Cadence Run shown in all five clips compared with two newly measured uncheckpointed executions of the same investigation protocol. Local synthetic incident/tools and real Qwen inference.','model':'qwen2.5:7b','cadence_workflow_id':run['workflow_id'],'cadence_run_id':run['run_id'],'cadence':cad,'raw':rawcounts,'request_equivalence':eq,'raw_execution':raw,'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (B.parent/'source').glob('*.py')},'cadence_receipts':str(state),'raw_receipts':str(root/'raw'),'actual_external_api_usd':0,'local_compute_cost_usd':None,'limits':['One observed interruption at an approval wait after all model/tool completions were recorded.','Input tokens include reported cached prompt tokens. Logical tokens are not a bill.','Raw baseline retains input/report side effects but no execution checkpoint. A checkpointed Python design can behave differently.','Presentation gates and log Activity heartbeats control capture pacing. Reviewer and approval Signals are sent by recorder automation.','A copied tool proposal is an explicit injection, not spontaneous model looping.']}
ct=cad['input_tokens']+cad['output_tokens'];rt=rawcounts['input_tokens']+rawcounts['output_tokens']
result.update(cadence_total_tokens=ct,raw_total_tokens=rt,token_reduction=(rt-ct)/rt,token_ratio=rt/ct)
save(root/'comparison.json',result)
print(json.dumps(result,indent=2))
