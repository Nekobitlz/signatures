import collections
import difflib
import json
from collections import defaultdict
from datetime import datetime

from music21 import converter
from music21 import environment

import lsh
import notes_utils
from json_utils import note_decoder, NoteEncoder
from notes_utils import should_skip
from signatures_lsh import SignaturesFinder

composer_to_color = {'Mozart': '#00FFFF',
                     'Schumann': '#FF00FF',
                     'Beethoven': '#00FF00',
                     'Haydn': '#0000FF',
                     'Tchaikovsky': '#FF0000',
                     'Vivaldi': '#FFFF00',
                     'Bach': '#800080',
                     'Schubert': '#FBA0E3',
                     'Chopin': '#FF1493',
                     'Glinka': '#FF4500'}


class ComposerFinder:

    def __init__(self, database_paths):
        self.database_signatures = {}
        for path in database_paths:
            with open(path) as json_file:
                self.database_signatures.update(json.load(json_file, object_hook=note_decoder))

    def run(self, score):
        transposed_score = notes_utils.transpose_to_c(score)
        transposed_notes = SignaturesFinder.__get_notes__(transposed_score)
        mapped_notes = SignaturesFinder.__map_notes__(transposed_notes, False)
        original_notes = SignaturesFinder.__pick_notes_from_score__(transposed_score)[0]

        shingles = []
        for i in range(6, 11):
            shingles.append(sum(SignaturesFinder(score, min_note_count=i).run(), []))
        shingles = sum(shingles, [])
        composer_count = {}
        composer_to_signatures = collections.defaultdict(list)
        for composer in self.database_signatures:
            signatures = self.database_signatures[composer][0]
            for signature in signatures:
                if signature in shingles:
                    composer_to_signatures[composer].append(signature)
        for composer in composer_to_signatures:
            composer_to_signatures[composer] = [composer_to_signatures[composer]]
        remove_duplicates_from(composer_to_signatures)
        for composer in composer_to_signatures:
            count = 0
            signatures = composer_to_signatures[composer][0]
            for signature in signatures:
                print('Composer {} has signature: {}'.format(composer, str(signature)))
                count = count + 1
                index = find_index(mapped_notes, signature)
                for note in range(index, index + len(signature)):
                    original_notes[note].style.color = composer_to_color[composer]
            if count > 0:
                composer_count[composer] = count
        signatures_count = sum(composer_count.values())
        composer_to_result = {}
        for composer in composer_count:
            composer_to_result[composer] = {'count': composer_count[composer],
                                            'confidence': composer_count[composer] / signatures_count * 100}
        print(composer_to_result)
        transposed_score.show()
        return composer_to_result


def remove_duplicates(database_paths):
    database_signatures = {}
    for path in database_paths:
        with open(path) as json_file:
            database_signatures.update(json.load(json_file, object_hook=note_decoder))
    remove_duplicates_from(database_signatures)
    with open(database_path, "w") as outfile:
        json.dump(database_signatures, outfile, cls=NoteEncoder)


def remove_duplicates_from(database_signatures):
    signatures_count = 0
    for key in database_signatures:
        val = database_signatures[key][0]
        signatures_count += len(val)
    count = 0
    to_remove = collections.defaultdict(list)
    start_time = datetime.now()
    threshold = 0.8
    items = list(database_signatures)
    for i in range(len(items)):
        val1 = database_signatures[items[i]][0]
        #print("Looking for composer {} by index {}".format(items[i], i))
        for j in range(i + 1, len(items)):
        #    print("Testing on composer {} by index {}".format(items[j], j))
            val2 = database_signatures[items[j]][0]
            for c1, notes1 in enumerate(val1):
                for c2, notes2 in enumerate(val2):
                    similarity = difflib.SequenceMatcher(None, notes1, notes2).ratio()
                    if similarity >= threshold:
                        to_remove[i].append(notes1)
                        to_remove[j].append(notes2)
                        # print("Needed to remove from {} - {} and from {} - {} with similarity: {}".format(items[i], notes1, items[j], notes2, similarity))
   # print("Time: {}".format(datetime.now() - start_time))
    for index in to_remove:
        tup = list(database_signatures.items())[index]
        for notes in to_remove[index]:
            if notes in tup[1][0]:
                tup[1][0].remove(notes)
                count += 1
   # print('Removed {} duplicates signatures from database of {}'.format(count, signatures_count))


def find_index(transposed_notes, shingle):
    index = 0
    shingle_index = 0
    while index < len(transposed_notes):
        if shingle_index == len(shingle):
            return index - len(shingle)
        if transposed_notes[index] == shingle[shingle_index]:
            index += 1
            shingle_index += 1
        else:
            index += 1
            shingle_index = 0
    return -1


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

database_path = 'res/dataset/no_repeats_signature_database-glinka.json'
remove = True
if remove:
    remove_duplicates([
        #'res/dataset/no_repeats_signature_database.json',
        'res/dataset/chopin/chopin.json',
        'res/dataset/glinka/glinka.json'
    ])
input_path = 'res/dataset/glinka/glinka-testing-set.json'

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
                finder_result = ComposerFinder([database_path]).run(note_score)
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
    counts = defaultdict(lambda: 0)
    for score in result:
        for composer in result[score]:
            counts[composer] += result[score][composer]['count']
    print(counts)

    with open(input_path + "-composer-result.json", "w") as outfile:
        json.dump(result, outfile)
    print('\nSearch ended')
