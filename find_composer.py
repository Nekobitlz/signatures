import collections
import itertools
import json

from music21 import converter

from json_utils import NoteEncoder, note_decoder


class ComposerFinder:

    def __init__(self, database_path):
        self.path = database_path
        with open(database_path) as json_file:
            expected_signatures = json.load(json_file, object_hook=note_decoder)
            print(expected_signatures)
        composer_signatures = {}
        for composer in expected_signatures:
            for signatures in expected_signatures[composer]:
                for signature in signatures:
                    print(signature)
        print(composer_signatures)



ComposerFinder('mozart.json')
