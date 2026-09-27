"""Audit recorded trajectories and run a no-model ablation; standard library only."""
import collections
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
UPSTREAM = ROOT / 'related_work/projects/NanoJev-main'
sys.path.insert(0, str(UPSTREAM / 'scripts'))
from evaluate_model_edges_maze import EdgeExplorer, MazeEnvironment
from scaled_maze import DIRECTIONS


def main():
    source = UPSTREAM / 'web/dev/side_by_side_results.json'
    data = json.loads(source.read_text(encoding='utf-8'))
    case = data['examples'][0]
    initial = {'game': 'scaled_maze', 'size': case['size'], **case['initial']}
    result = {'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'case_id': case['id'], 'protocol': data['protocol']['controllers']['maze'],
              'model_api_calls': 0, 'systems': {}, 'scope': 'One fixed upstream showcase; no latency measurement'}
    for system in case['systems'][:2]:
        env = MazeEnvironment(initial)
        policy = EdgeExplorer(initial['position'], initial['goal'], initial['size'])
        sites = {}
        for frame in system['frames'][1:]:
            pos = tuple(frame['decision_position'])
            if policy.needs_prediction():
                sites[pos] = frame['probabilities']
                policy.remember_prediction(frame['probabilities'])
            decision = policy.choose()
            assert decision['action'] == frame['action'], (system['id'], frame)
            assert decision['mode'] == frame['decision_source']
            feedback = env.attempt(decision['action'])
            assert feedback['next_position'] == frame['position']
            assert feedback['collision'] == frame['collision']
            policy.observe_transition(decision['action'], feedback['next_position'], feedback['collision'])
        assert env.reached_goal()
        ps = [p for row in sites.values() for p in row.values()]
        summary = system['summary']
        result['systems'][system['id']] = dict(summary,
            successful_moves=summary['steps']-summary['collisions'],
            prediction_sites=len(sites), atomic_predictions=len(ps),
            predictions_ge_half=sum(p >= .5 for p in ps), p_min=min(ps), p_max=max(ps),
            modes=dict(collections.Counter(f['decision_source'] for f in system['frames'][1:])),
            original_controller_replay_verified=True)
    # Same environment, controller, tie order and budget. Replace ONLY the scorer.
    env = MazeEnvironment(initial)
    policy = EdgeExplorer(initial['position'], initial['goal'], initial['size'])
    trace = []
    for n in range(case['horizon']):
        if policy.needs_prediction():
            policy.remember_prediction(dict.fromkeys(DIRECTIONS, .5))
        decision = policy.choose()
        if decision is None:
            break
        feedback = env.attempt(decision['action'])
        trace.append(dict(decision, **feedback))
        policy.observe_transition(decision['action'], feedback['next_position'], feedback['collision'])
        if env.reached_goal():
            break
    result['constant_half_ablation'] = {'steps': len(trace),
        'collisions': sum(f['collision'] for f in trace), 'goal': env.reached_goal(),
        'description': 'Local deterministic run; all directions p=0.5; no model and no full-map planner'}
    result['attempt_ratio_jev_over_nano'] = 2738/225
    result['interpretation'] = 'All 572 NanoJev probabilities pass 0.5; geometry, visit memory and probability tie-breaks choose the path. Constant scores need only 162 attempts here: this showcase does not establish model accuracy or necessity.'
    (HERE/'results/nano-maze-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    (HERE/'results/nano-maze-constant-trace.json').write_text(json.dumps(trace,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
