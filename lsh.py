from itertools import combinations

import numpy as np


class LSH:

    def __init__(self, b):
        self.b = b
        self.buckets = []
        self.counter = 0
        for i in range(b):
            self.buckets.append({})

    def make_subvecs(self, signature):
        l = len(signature)
        assert l % self.b == 0
        r = int(l / self.b)
        # break signature into subvectors
        subvecs = []
        for i in range(0, l, r):
            subvecs.append(signature[i:i + r])
        return np.stack(subvecs)

    def add_hash(self, signature):
        subvecs = self.make_subvecs(signature).astype(str)
        for i, subvec in enumerate(subvecs):
            subvec = ','.join(subvec)
            if subvec not in self.buckets[i].keys():
                self.buckets[i][subvec] = []
            self.buckets[i][subvec].append(self.counter)
        self.counter += 1

    def check_candidates(self, min_signature_entries, max_signature_entries):
        candidates = []
        for bucket_band in self.buckets:
            keys = bucket_band.keys()
            for bucket in keys:
                hits = bucket_band[bucket]
                if min_signature_entries <= len(hits) <= max_signature_entries:
                    candidates.extend(combinations(hits, len(hits)))
                    # candidates.extend(tuple(hits))
                    # todo методы подбора комбинаций
        return set(candidates)
