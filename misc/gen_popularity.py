import csv
import json
import seaborn as sbn
import numpy as np

"""
Add a popularity_metrics column with some fake data into the sample data CSV.
"""

def gen_dist(_max):
    num_samples = 5000
    population = np.random.pareto(num_samples, num_samples)
    highest = max(population)
    scale = _max / highest
    _sorted = sorted(population * scale)
    return [int(n) for n in _sorted]


likes, views, comments = gen_dist(1000000), gen_dist(4000000), gen_dist(30000)

with open('sample_data.csv') as _csv, open('enriched.csv', 'w+') as out:
    reader = csv.DictReader(_csv)
    writer = csv.DictWriter(out, fieldnames=reader.fieldnames)
    writer.writeheader()
    enriched = []
    for idx, row in enumerate(reader):
        metadata = json.loads(row['meta_data'])
        fake = {'likes': likes[idx], 'views': views[idx], 'comments': comments[idx]}
        metadata['popularity_metrics'] = fake
        row['meta_data'] = json.dumps(metadata)
        writer.writerow(row)

