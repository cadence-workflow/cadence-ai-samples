"""Check the frozen synthetic recording without services or model calls."""
from pathlib import Path
import base64
import hashlib
import json
import sqlite3

HERE = Path(__file__).resolve().parent

def read(path):
    return json.loads((HERE / path).read_text())

def rows(path):
    return [json.loads(line) for line in (HERE / path).read_text().splitlines() if line]

def payload(value):
    return json.loads(base64.b64decode(value['data']))

def verify():
    manifest = read('source-manifest.json')
    for name, expected in manifest['files'].items():
        actual = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        assert actual == expected['export_sha256'], f'Export hash changed: {name}'
        if expected['byte_identical']:
            assert actual == expected['original_sha256'], name
    run = read('recorded/run.json')
    summary = read('recorded/comparison.json')
    history = read('recorded/final-history.json')
    events = {int(event['event_id']): event for event in history}
    assert sorted(events) == list(range(1, 202)), 'Missing or unexpected events'
    start = events[1]['workflow_execution_started_event_attributes']
    assert start['original_execution_run_id'] == run['run_id'] == summary['cadence_run_id']
    assert start['task_list']['name'] == run['workflow_id'] == summary['cadence_workflow_id']
    inputs = payload(start['input'])
    assert inputs['limits']['presentation_mode'] and inputs['limits']['inject_duplicate']
    assert inputs['limits']['repeat_limit'] == 1
    assert json.loads(inputs['text'])['synthetic'] is True

    policy = events[25]['activity_task_scheduled_event_attributes']['retry_policy']
    assert policy['initial_interval'] == policy['maximum_interval'] == '10s'
    assert policy['maximum_attempts'] == 3
    assert 'NonRetryableHttpError' in policy['non_retryable_error_reasons']
    assert events[32]['activity_task_started_event_attributes']['attempt'] == 1
    ledger = rows('recorded/cadence/ledger.jsonl')
    gateway = [item for item in ledger if item['tool']=='get_logs_by_trace_id' and item['service']=='api-gateway']
    assert [(item['attempt'],item['status']) for item in gateway] == [(0,429),(1,200)]
    assert sum(item['tool']=='fetch_dependency_graph' for item in ledger) == 1

    for event_id, name in [(95,'revise'),(105,'guidance'),(180,'revise'),(190,'approval')]:
        assert events[event_id]['workflow_execution_signaled_event_attributes']['signal_name'] == name
    first_revision = payload(events[101]['activity_task_completed_event_attributes']['result'])
    assert first_revision['confidence'] == 'high'
    new_lookups = [event for event in history if 95 < int(event['event_id']) < 105
        and event.get('activity_task_scheduled_event_attributes',{}).get('activity_type',{}).get('name') == 'incident-triage.get-logs']
    assert not new_lookups, 'Unexpected new evidence during first revision'
    final = payload(events[186]['activity_task_completed_event_attributes']['result'])
    assert final['root_cause'] == 'unknown' and final['confidence'] == 'low'
    assert final == read('recorded/final-report.json') == run['state']['conclusion']
    commit = events[197]['activity_task_completed_event_attributes']
    assert commit['identity'] == 'activities-B' and payload(commit['result'])['committed'] is True
    completion = payload(events[201]['workflow_execution_completed_event_attributes']['result'])
    assert completion['outcome'] == 'conclusion_uploaded' and completion['conclusion'] == final
    proposal = run['state']['injected_proposal']
    assert proposal['model_generated'] is False and proposal['executed'] is False
    assert 'deliberate fault injection' in proposal['source']

    all_requests = {}
    observed = {}
    for phase, count in [('cadence',9),('raw',18)]:
        usage = rows(f'recorded/{phase}/model-spend.jsonl')
        responses = rows(f'recorded/{phase}/model-responses.jsonl')
        ledger = rows(f'recorded/{phase}/ledger.jsonl')
        assert len(usage) == len(responses) == count
        tokens_in = sum(item['input_tokens'] for item in usage)
        tokens_out = sum(item['output_tokens'] for item in usage)
        assert tokens_in == sum(item['response']['usage']['prompt_tokens'] for item in responses)
        assert tokens_out == sum(item['response']['usage']['completion_tokens'] for item in responses)
        assert summary[phase]['input_tokens'] == tokens_in
        assert summary[phase]['output_tokens'] == tokens_out
        invocations = sum(item['tool'] in ('plan_next','revise_draft') for item in ledger)
        assert invocations == count
        assert sum(item['tool']=='upload_conclusion' and item.get('committed') is True for item in ledger) == 1
        database = HERE / 'recorded' / phase / 'store.db'
        with sqlite3.connect(database.as_uri() + '?mode=ro', uri=True) as db:
            assert db.execute('select count(*) from conclusions').fetchone()[0] == 1
        all_requests[phase] = [item['request'] for item in responses]
        observed[phase] = {'responses':count,'input_tokens':tokens_in,'output_tokens':tokens_out,'total_tokens':tokens_in+tokens_out}
    assert all_requests['cadence'] == all_requests['raw'][:9] == all_requests['raw'][9:]
    assert observed['cadence']['total_tokens'] == 4652
    assert observed['raw']['total_tokens'] == 9304
    stopped = read('recorded/owned-workers-stopped.json')
    restored = read('recorded/owned-workers-restarted.json')
    assert stopped['pids_alive'] == [] and len(restored['pids']) == 2
    assert stopped['run_id'] == restored['run_id'] == run['run_id']
    assert stopped['usage'] == restored['usage'] == run['usage']
    assert run['service_completed'] and run['state']['phase'] == 'DONE'
    for name, values in manifest['files'].items():
        if name.startswith('source/') and name.endswith('.py'):
            assert values['original_sha256'] == summary['source_sha256'][Path(name).name]
    return {'checks':'PASS','frozen_files':len(manifest['files']), 'events':len(history),
        'workflow_id':run['workflow_id'],'run_id':run['run_id'], 'observed':observed,
        'recovery_model_responses':0, 'token_reduction':0.5,
        'scope':'Offline verification of saved synthetic evidence. No provider or Cadence calls.'}

if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
