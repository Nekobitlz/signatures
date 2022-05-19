import itertools

from music21 import converter, note
from music21.stream import Stream

from signatures_lsh import SignaturesFinder


class MultiScoreSignatures:

    def __init__(self, scores):
        signatures = []
        use_rhythmic = False
        for score in scores:
            sf = SignaturesFinder(score)
            signatures.append(sf.run())
        mapped_signatures = []
        for scope_signatures in signatures:
            mapped_scope_signatures = []
            for signatures_entry in scope_signatures:
                for signature in signatures_entry:
                    mapped_signature = SignaturesFinder.__map_notes__(signature, use_rhythmic)
                    if mapped_signature not in mapped_scope_signatures:
                        mapped_scope_signatures.append(mapped_signature)
            mapped_signatures.append(mapped_scope_signatures)
        print(mapped_signatures)
        score_index_const = 1000
        pair_labels = []
        for x1, x2 in itertools.combinations(zip(range(len(mapped_signatures)), mapped_signatures), 2):
            for y1, y2 in itertools.product(zip(range(len(x1[1])), x1[1]), zip(range(len(x2[1])), x2[1])):
                if y1[1] == y2[1]:
                    print(y1[1])
                    x1key = x1[0] * score_index_const + y1[0]
                    x2key = x2[0] * score_index_const + y2[0]
                    pair_labels.append((x1key, x2key))
        print(pair_labels)
        groups = {}
        for (x, y) in pair_labels:
            xset = groups.get(x, {x})
            yset = groups.get(y, {y})
            jset = xset | yset
            for z in jset:
                groups[z] = jset
        multi_score_signatures = set(map(tuple, groups.values()))
        print(multi_score_signatures)
        mapped_multi_score_signatures = []
        for entry in multi_score_signatures:
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
        print(mapped_multi_score_signatures)

        for score_signatures in mapped_multi_score_signatures:
            stream1 = Stream()
            for signatures in score_signatures:
                for notes in signatures:
                    for note1 in notes:
                        stream1.append(note1)
                    stream1.append(note.Rest())
                    stream1.append(note.Rest())
                stream1.append(note.Rest())
                stream1.append(note.Rest())
                stream1.append(note.Rest())
            stream1.show()


# score1 = converter.parse('https://kern.humdrum.org/cgi-bin/ksdata?location=users/craig/classical/bach/371chorales&file=chor279.krn&f=kern')
score2 = converter.parse('tinyNotation: 4/4 d c B A d c B A d c B A d c B A')
score1 = converter.parse(
    'https://kern.humdrum.org/cgi-bin/ksdata?location=users/craig/classical/mozart/piano/sonata&file=sonata10-2.krn&format=kern&o=norep')
score3 = converter.parse(
    'https://kern.humdrum.org/cgi-bin/ksdata?location=users/craig/classical/mozart/piano/sonata&file=sonata03-2.krn&format=kern')
score4 = converter.parse('https://kern.humdrum.org/cgi-bin/ksdata?location=musedata/mozart/quartet&file=k080-01.krn&format=kern')
score5 = converter.parse('https://kern.humdrum.org/cgi-bin/ksdata?location=musedata/mozart/quartet&file=k155-01.krn&format=kern')
score6 = converter.parse('https://kern.humdrum.org/cgi-bin/ksdata?location=musedata/mozart/quartet&file=k156-01.krn&format=kern')
score7 = converter.parse('https://kern.humdrum.org/cgi-bin/ksdata?location=musedata/mozart/quartet&file=k157-01.krn&format=kern')

MultiScoreSignatures([score1, score2, score3, score4, score5, score6, score7])
