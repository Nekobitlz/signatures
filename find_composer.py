import json

from music21 import converter
from music21 import environment

from json_utils import note_decoder
from notes_utils import should_skip
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
        shingles = []
        for i in range(6, 11):
            shingles.append(sum(SignaturesFinder(score, min_note_count=i).run(), []))
        shingles = sum(shingles, [])
        composer_count = {}
        for composer in self.database_signatures:
            count = 0
            signatures = self.database_signatures[composer][0]
            for signature in signatures:
                if signature in shingles:
                    count = count + 1
            if count > 0:
                composer_count[composer] = count
        signatures_count = sum(composer_count.values())
        for composer in composer_count:
            print('{}: {} %'.format(composer, composer_count[composer] / signatures_count * 100))
        composer_to_result = {}
        for composer in composer_count:
            composer_to_result[composer] = {'count': composer_count[composer],
                                            'confidence': composer_count[composer] / signatures_count * 100}
        print(composer_to_result)
        return composer_to_result


def get_composer_with_max(finder_result):
    max_value = -1
    max_key = ""
    for founded_composer in finder_result:
        value = finder_result[founded_composer]['count']
        if value > max_value:
            max_value = value
            max_key = founded_composer
    return max_key


e = environment.Environment()
e['autoDownload'] = 'allow'

finder = ComposerFinder(['res/scores/cortical-algorithms/bach-control-set.json',
                         'res/scores/cortical-algorithms/beethoven-control-set.json',
                         'res/scores/cortical-algorithms/chopin-control-set-1.json',
                         'res/scores/cortical-algorithms/corelli-control-set.json',
                         'res/scores/cortical-algorithms/haydn-control-set.json',
                         'res/scores/cortical-algorithms/joplin-control-set-1.json',
                         'res/scores/cortical-algorithms/mozart-control-set.json',
                         'res/scores/cortical-algorithms/scarlatti-control-set.json',
                         'res/scores/cortical-algorithms/vivaldi-control-set-1.json',
                         ])
input_path = 'res/scores/cortical-algorithms/mozart-control-set-testing-set.json'

with open(input_path) as test_scores:
    comp_to_scores = json.load(test_scores)
    result = {}
    correct_results = 0
    score_count = 0
    for composer in comp_to_scores:
        current_correct = 0
        for score in comp_to_scores[composer]:
            if should_skip(score):
                continue
            try:
                note_score = converter.parse(score.rstrip())
                print('\nStarting search in ', score)
                finder_result = finder.run(note_score)
                found_composer = get_composer_with_max(finder_result)
                if composer == get_composer_with_max(finder_result):
                    current_correct = current_correct + 1
                score_count += 1
                result[score] = finder_result
            except Exception as ex:
                print('Failed parsing for {} due to exception: {}'.format(score, ex))
        correct_results += current_correct
        print('Got {}% for {}'.format(current_correct / len(comp_to_scores[composer]) * 100, composer))
    print('Finally got {}% for all'.format(correct_results / score_count * 100))

    with open(input_path + "-composer-result.json", "w") as outfile:
        json.dump(result, outfile)
    print('\nSearch ended')
