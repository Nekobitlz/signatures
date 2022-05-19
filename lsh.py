import itertools


class LSH:

    def check_candidates(self, doc_shingles, equal_count, min_signature_entries, max_signature_entries):
        pair_labels = []
        for x1, x2 in itertools.combinations(zip(range(len(doc_shingles)), doc_shingles), 2):
            similarity = self.similarity(equal_count, x1[1], x2[1])
            if similarity >= equal_count:
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

    def similarity(self, target_equal_count, sig_a, sig_b):
        equal_count = len(sig_a)
        for i in range(0, len(sig_a)):
            if sig_a[i] != sig_b[i]:
                equal_count = equal_count - 1
            if equal_count < target_equal_count:
                break
        return equal_count
