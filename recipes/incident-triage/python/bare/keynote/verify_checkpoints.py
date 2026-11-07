"""Validate playback checkpoints against the frozen history and clip metadata."""
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent


def verify():
    checkpoints = json.loads((HERE / 'checkpoints.json').read_text())
    history = json.loads((HERE / 'recorded' / 'final-history.json').read_text())
    run = json.loads((HERE / 'recorded' / 'run.json').read_text())
    comparison = json.loads((HERE / 'recorded' / 'comparison.json').read_text())
    events = {int(event['event_id']): event for event in history}

    assert checkpoints['workflow_id'] == run['workflow_id'] == comparison['cadence_workflow_id']
    assert checkpoints['run_id'] == run['run_id'] == comparison['cadence_run_id']
    assert checkpoints['step_history'] == ['Trace', 'Graph', 'Logs', 'Draft', 'Review', 'Save']

    clip_by_id = {clip['id']: clip for clip in checkpoints['clips']}
    assert [clip['slide'] for clip in checkpoints['clips']] == [18, 21, 24, 27, 30]

    measured = checkpoints['measured_comparison']
    assert measured['show_before'] == 'reset'
    assert measured['cadence_same_run_recovery']['model_responses'] == 9
    assert measured['cadence_same_run_recovery']['logical_tokens'] == 4652
    assert measured['python_restart']['model_responses'] == 18
    assert measured['python_restart']['logical_tokens'] == 9304
    assert checkpoints['reset']['introduce_after'] == 'measured_comparison'
    assert checkpoints['production_observation']['separate_from_demo'] is True

    ids = [item['id'] for item in checkpoints['checkpoints']]
    assert ids == [
        'setup-and-agent-map',
        'lookup-fails-then-recovers',
        'read-returned-evidence',
        'copied-lookup-blocked',
        'first-diagnosis-incomplete',
        'confidence-not-new-evidence',
        'human-guidance-changes-path',
        'workers-stop-at-approval',
        'same-run-recovery',
    ]

    for item in checkpoints['checkpoints']:
        for event_id in item.get('history_events') or []:
            assert event_id in events, f"missing event {event_id} for {item['id']}"
        recording = item.get('recording')
        if recording is None:
            continue
        clip = clip_by_id[recording['clip_id']]
        assert recording['slide'] == clip['slide']
        assert 0 <= recording['seek_s'] <= clip['duration_s'] + 0.01, item['id']

    # Spot-check signal and completion names used in teaching checkpoints.
    assert events[95]['workflow_execution_signaled_event_attributes']['signal_name'] == 'revise'
    assert events[105]['workflow_execution_signaled_event_attributes']['signal_name'] == 'guidance'
    assert events[190]['workflow_execution_signaled_event_attributes']['signal_name'] == 'approval'
    assert 'workflow_execution_completed_event_attributes' in events[201]

    proposal = run['state']['injected_proposal']
    assert proposal['model_generated'] is False and proposal['executed'] is False

    return {
        'checks': 'PASS',
        'checkpoints': len(checkpoints['checkpoints']),
        'clips': len(checkpoints['clips']),
        'workflow_id': checkpoints['workflow_id'],
        'run_id': checkpoints['run_id'],
        'scope': 'Offline validation of playback checkpoints against frozen history.',
    }


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
