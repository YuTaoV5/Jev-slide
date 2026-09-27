"""Reproduce the application decision from existing, explicitly artificial fixtures."""
from pathlib import Path
import hashlib
import json
import numpy as np

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'jev_practice' / 'results' / 'jevfire.json'
source = json.loads(SOURCE.read_text(encoding='utf-8-sig'))
assert source['mode'] == 'offline-artificial-logprobs' and source['model'] is None
scores = np.asarray([r['artificial_scores'] for r in source['records']], dtype=float)
threshold = float(source['request']['min_probability'])
labels = np.asarray(source['request']['schema']['route']['choices'])
selected = np.argmax(scores, axis=1)
top = scores[np.arange(len(scores)), selected]
accept = top >= threshold
assert np.allclose(scores.sum(axis=1), 1.0)
assert np.allclose(scores, [[.82, .12, .06], [.36, .34, .30]])
for i, record in enumerate(source['records']):
    assert bool(accept[i]) != record['decision']['abstained']
    assert str(labels[selected[i]]) == record['decision']['selected_value']
data = HERE / 'data'
data.mkdir(exist_ok=True)
np.savez(data / 'data.npz', scores=scores, threshold=threshold, labels=labels,
         selected=selected, top=top, accept=accept)
report = dict(source=str(SOURCE), source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              mode='offline-artificial-fixture', model_run=False, api_calls=0,
              source_field='records[*].artificial_scores', scores=scores.tolist(),
              threshold=threshold, rule='max(probabilities) >= threshold',
              outcomes=['billing' if x else 'human_review' for x in accept],
              caveat='max probability is not the TypeSafe confidence field')
(data / 'provenance.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
