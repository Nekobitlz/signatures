import collections
import itertools

import numpy as np
from music21 import converter, note
from music21.stream import Stream

from signatures_lsh import SignaturesFinder


class MultiScoreSignatures:

    def __init__(self):
        self.b = 1
        self.buckets = []
        for i in range(self.b):
            self.buckets.append({})

    def run(self, scores):
        signatures = []
        use_rhythmic = False
        for score in scores:
            sf = SignaturesFinder(score)
            signatures.append(sf.run())
        mapped_signatures = []
        for scope_signatures in signatures:
            mapped_scope_signatures = []
            for signatures_entry in scope_signatures:
                mapped_signature = []
                for signature in signatures_entry:
                    mapped_notes = SignaturesFinder.__map_notes__(signature, use_rhythmic)
                    if mapped_notes not in mapped_signature:
                        mapped_signature.append(mapped_notes)
                mapped_scope_signatures.append(mapped_signature)
            mapped_signatures.append(mapped_scope_signatures)
        print(mapped_signatures)
        score_index_const = 1000
        for i in range(0, len(mapped_signatures)):
            mapped_scope_signatures = mapped_signatures[i]
            for j in range(0, len(mapped_scope_signatures)):
                for notes in mapped_scope_signatures[j]:
                    key = i * score_index_const + j
                    self.add_hash(notes, key)
        candidates = self.check_candidates()
        print(candidates)
        mapped_multi_score_signatures = []
        for entry in candidates:
            current_signatures = []
            for el in entry:
                index = int(el / score_index_const)
                signature_index = int(el - index * score_index_const)
                real = []
                for notes in signatures[index][signature_index]:
                    if notes not in real:
                        real.append(notes)
                current_signatures.append(real)
            mapped_multi_score_signatures.append(current_signatures)

        for score_signatures in mapped_multi_score_signatures:
            stream1 = Stream()
            for signatures in score_signatures:
                for notes in signatures:
                    for note1 in notes:
                        if note1 not in stream1:
                            stream1.append(note1)
                    stream1.append(note.Rest())
                    stream1.append(note.Rest())
                stream1.append(note.Rest())
                stream1.append(note.Rest())
                stream1.append(note.Rest())
            stream1.show()
        return mapped_multi_score_signatures

    def make_subvecs(self, signature):
        l = len(signature)
        assert l % self.b == 0
        r = int(l / self.b)
        # break signature into subvectors
        subvecs = []
        for i in range(0, l, r):
            subvecs.append(signature[i:i + r])
        return np.stack(subvecs)

    def add_hash(self, signature, index):
        subvecs = self.make_subvecs(signature).astype(str)
        for i, subvec in enumerate(subvecs):
            subvec = ','.join(subvec)
            if subvec not in self.buckets[i].keys():
                self.buckets[i][subvec] = []
            self.buckets[i][subvec].append(index)

    def check_candidates(self):
        candidates = []
        for bucket_band in self.buckets:
            keys = bucket_band.keys()
            for bucket in keys:
                hits = bucket_band[bucket]
                if len(hits) > 1:
                    candidates.extend(itertools.combinations(hits, len(hits)))
        return set(candidates)
