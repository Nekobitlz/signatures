import collections
import json

from music21 import environment
from music21 import converter

from json_utils import NoteEncoder, note_decoder
from multi_score_signatures import MultiScoreSignatures
from notes_utils import should_skip


class ComposerSignatures:

    def __init__(self, path):
        self.path = path
        scores = collections.defaultdict(list)
        with open(path) as f:
            lines = f.readlines()
            for line in lines:
                if should_skip(line):
                    continue
                try:
                    note_score = converter.parse(line.rstrip())
                    if note_score.metadata is not None and note_score.metadata.composer is not None:
                        scores[note_score.metadata.composer].append(note_score)
                    else:
                        scores['Unknown'].append(note_score)
                        print('Not found composer in metadata: ', line)
                    print('Parsed ', line)
                except Exception as ex:
                    print('Failed parsing for {} due to exception: {}'.format(line, ex))

        result = collections.defaultdict(list)
        for composer in scores:
            multi_score_signatures = MultiScoreSignatures().run(scores[composer])
            result[composer].append(multi_score_signatures)

        with open(path + ".json", "w") as outfile:
            json.dump(result, outfile, cls=NoteEncoder)
        with open(path + ".json") as json_file:
            data = json.load(json_file, object_hook=note_decoder)
            print(data)


e = environment.Environment()
e['autoDownload'] = 'allow'


ComposerSignatures('res/scores/cortical-algorithms/mozart-control-set')
