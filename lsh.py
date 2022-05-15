import itertools

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

    def check_candidates(self, doc_shingles, threshold, min_signature_entries, max_signature_entries):
        pair_labels = []
        for x1, x2 in itertools.combinations(zip(range(len(doc_shingles)), doc_shingles), 2):
            similarity = self.similarity(x1[1], x2[1])
            if similarity >= (100 - threshold) / 100:
                pair_labels.append((x1[0], x2[0]))
        return self.make_equiv_classes(pair_labels, min_signature_entries, max_signature_entries)

    def make_equiv_classes(self, pairs, min_signature_entries, max_signature_entries):
        groups = {}
        for (x, y) in pairs:
            xset = groups.get(x, {x})
            yset = groups.get(y, {y})
            jset = xset | yset
            for z in jset:
                groups[z] = jset
        filtered_groups = []
        for group in groups.values():
            if min_signature_entries <= len(group) <= max_signature_entries:
                filtered_groups.append(group)
        return set(map(tuple, filtered_groups))

    def similarity(self, sig_a, sig_b):
        equal_count = 0
        for i in range(0, len(sig_a)):
            if sig_a[i] == sig_b[i]:
                equal_count = equal_count + 1
        return equal_count / len(sig_a)
