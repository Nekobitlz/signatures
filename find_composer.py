import collections
import json

from music21 import converter

from json_utils import NoteEncoder, note_decoder
from notes_utils import transpose_to_c
from signatures_lsh import SignaturesFinder
# багнутая - 'https://kern.humdrum.org/cgi-bin/ksdata?location=musedata/mozart/quartet&file=k161-01.krn&format=kern'
score = converter.parse('https://kern.humdrum.org/cgi-bin/ksdata?location=musedata/mozart/quartet&file=k285-01.krn&format=kern')


class ComposerFinder:

    def __init__(self, score, database_paths):
        expected_signatures = {}
        for path in database_paths:
            with open(path) as json_file:
                expected_signatures.update(json.load(json_file, object_hook=note_decoder))
        temp = []
        buckets = {}
        # expected_signatures = collections.defaultdict(list)
        score_index_const = 100000
        for i, el in enumerate(expected_signatures.items()):
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
                tup = list(expected_signatures.items())[composer_index]
                tup[1][0].remove(element)
        print('Removed {} duplicates signatures from database'.format(len(to_remove)))

        self.transposed_score = transpose_to_c(score)
        self.transposed_notes = SignaturesFinder.__get_notes__(self.transposed_score)
        notes = SignaturesFinder.__map_notes__(self.transposed_notes, False)
        shingles = SignaturesFinder.getShingles(notes, 5)
        composer_count = {}
        for composer in expected_signatures:
            count = 0
            signatures = expected_signatures[composer][0]
            for signature in signatures:
                if signature in shingles:
                    count = count + 1
            if count > 0:
                composer_count[composer] = count
        print(composer_count)
        signatures_count = sum(composer_count.values())
        for composer in composer_count:
            print('{}: {} %'.format(composer, composer_count[composer] / signatures_count * 100))


ComposerFinder(score, ['res/bach_short.json', 'res/mozart_short.json'])
