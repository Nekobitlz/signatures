import collections
import json

from music21 import converter

from json_utils import note_decoder
from signatures_lsh import SignaturesFinder
# багнутая - 'https://kern.humdrum.org/cgi-bin/ksdata?location=musedata/mozart/quartet&file=k161-01.krn&format=kern'


class ComposerFinder:

    def __init__(self, database_paths):
        self.database_signatures = {}
        for path in database_paths:
            with open(path) as json_file:
                self.database_signatures.update(json.load(json_file, object_hook=note_decoder))
        buckets = {}
        score_index_const = 100000
        for i, el in enumerate(self.database_signatures.items()):
            key, val = el
            for j, notes in enumerate(val[0]):
                subvec = ','.join(map(str, notes))
                composer_index = i * score_index_const + j
                if subvec not in buckets:
                    buckets[subvec] = []
                buckets[subvec].append(composer_index)
        to_remove = []
        for el in buckets.items():
            if len(el[1]) > 1:
                to_remove.append(el)
        for scores in to_remove:
            element = list(map(int, scores[0].split(',')))
            for indexes in scores[1]:
                composer_index = int(indexes / score_index_const)
                tup = list(self.database_signatures.items())[composer_index]
                tup[1][0].remove(element)
        print('Removed {} duplicates signatures from database'.format(len(to_remove)))

    def run(self, score):
        shingles = sum(SignaturesFinder(score).run(), [])
        composer_count = {}
        for composer in self.database_signatures:
            count = 0
            signatures = self.database_signatures[composer][0]
            for signature in signatures:
                if signature in shingles:
                    count = count + 1
            if count > 0:
                composer_count[composer] = count
        print(composer_count)
        signatures_count = sum(composer_count.values())
        for composer in composer_count:
            print('{}: {} %'.format(composer, composer_count[composer] / signatures_count * 100))


finder = ComposerFinder(['res/bach_short.json', 'res/mozart_short.json'])
path = ''
with open('res/scores/test_scores') as test_scores:
    lines = test_scores.readlines()
    for line in lines:
        if line.startswith('#'):
            continue
        note_score = converter.parse(line.rstrip())
        print('\nStarting search in ', line)
        finder.run(note_score)
