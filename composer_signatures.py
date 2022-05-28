import collections
import json

from music21 import converter

from json_utils import NoteEncoder, note_decoder
from multi_score_signatures import MultiScoreSignatures


class ComposerSignatures:

    def __init__(self, path):
        self.path = path
        scores = collections.defaultdict(list)
        with open(path) as f:
            lines = f.readlines()
            for line in lines:
                note_score = converter.parse(line)
                scores[note_score.metadata.composer].append(note_score)

        result = collections.defaultdict(list)
        for composer in scores:
            multi_score_signatures = MultiScoreSignatures().run(scores[composer])
            result[composer].append(multi_score_signatures)
        for res in result:
            print(str(res) + ':' + str(result[res]))

        with open("mozart.json", "w") as outfile:
            json.dump(result, outfile, cls=NoteEncoder)
        with open('mozart.json') as json_file:
            data = json.load(json_file, object_hook=note_decoder)
            print(data)


ComposerSignatures('res/mozart.txt')
