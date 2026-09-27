"""No network or model inference: execute upstream decision code and audit recordings."""
import hashlib
import importlib.util
import json
import math
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROJECTS = ROOT / 'related_work/projects'
OUT = HERE / 'results'
OUT.mkdir(exist_ok=True)

def save(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    subprocess.run(['node', str(HERE / 'compaction.mjs')], check=True)
    sys.path.insert(0, str(PROJECTS / 'jevfire-main'))
    from jevfire.core import Label, decode_choice, BackendError
    from jevfire.models import DecisionRequest
    request = DecisionRequest.model_validate({'context':'合成工单：重复扣款，请协助退款。',
        'schema': {'route': {'type':'enum', 'description':'Select a support queue',
            'choices':['billing','technical','unknown']}}, 'min_probability':0.7})
    labels = [Label('A', 11), Label('B', 12), Label('C', 13)]
    records = []
    for scores in ([.82,.12,.06], [.36,.34,.30]):
        raw = {'logprobs':{'top_logprobs':[{f'token_id:{label.token_id}':math.log(p)
            for label,p in zip(labels,scores)}]}}
        decision = decode_choice(raw, request.fields['route'], labels, request)
        records.append({'artificial_scores':scores,'raw_fixture':raw,'decision':decision})
    assert records[0]['decision']['value'] == 'billing'
    assert records[1]['decision']['value'] is None
    try:
        decode_choice({'logprobs':{'top_logprobs':[{}]}}, request.fields['route'], labels, request)
    except BackendError:
        missing_score_rejected = True
    else:
        raise AssertionError('Missing scores must fail')
    save('jevfire.json', {'mode':'offline-artificial-logprobs','model':None,'api_calls':0,
        'request':request.model_dump(by_alias=True),'records':records,
        'missing_score_rejected':missing_score_rejected,
        'limitation':'Exercises upstream decoder, not tokenizer, GPU, model quality or calibration.'})
    q = load_module('jarvis_questions', PROJECTS / 'jev-chat-jarvis-main/tools/jev/questions.py')
    messages = [('her','明天下午三点前能把演示文稿发我吗？'),('me','我确认一下进度。')]
    state = q.build_state(messages, '同事')
    candidates = ['我先确认进度，再给你准确时间。','早就发了，你自己找。','一定完成所有需求，绝不延期。']
    rank = q.build_rank_question(candidates)
    assert len(q.JUDGE_QUESTIONS) == 7
    assert list(rank['best_reply']['criteria'].values()) == candidates
    assert len(q.build_state([('her',str(i)) for i in range(15)],'同事')['chat']['messages']) == 10
    try:
        q.build_rank_question(candidates[:2])
    except ValueError:
        pass
    else:
        raise AssertionError('Exactly three candidates required')
    save('jarvis.json', {'mode':'request-construction-only','api_calls':0,'state':state,
        'judge_questions':q.JUDGE_QUESTIONS,'rank_questions':rank,
        'limitation':'Human-written candidates; no generated reply, model answer, ranking or Android run.'})
    recording = PROJECTS / 'NanoJev-main/web/dev/side_by_side_results.json'
    data = json.loads(recording.read_text(encoding='utf-8'))
    examples=[]
    for example in data['examples']:
        systems=[]
        for system in example['systems']:
            assert system['frames'], 'Recording must contain frames'
            systems.append({'id':system['id'],'summary':system['summary'],
                            'frame_count':len(system['frames'])})
        examples.append({'id':example['id'],'game':example['game'],'seed':example.get('seed'),
                         'systems':systems})
    save('nanojev.json', {'mode':'upstream-recording-audit','api_calls':0,
        'source_sha256':hashlib.sha256(recording.read_bytes()).hexdigest(),
        'protocol':data['protocol'],'examples':examples,
        'limitation':'Upstream recordings; metadata and browser replay checked, not new inference or independent simulator validation.'})
    archives=[{'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
               'bytes':p.stat().st_size} for p in sorted((ROOT/'related_work').glob('*.zip'))]
    save('manifest.json', {'timestamp':datetime.now(timezone.utc).isoformat(),
         'python':platform.python_version(),'platform':platform.platform(),'archives':archives,
         'scope':'Offline teaching demonstrations; not a research benchmark.', 'api_calls':0,'cost_usd':0})
    print('PASS: compaction, JEVfire decoding/abstention, Jarvis question construction, NanoJev recording audit')

if __name__ == '__main__':
    main()
