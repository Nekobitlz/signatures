from music21 import converter

from find_signatures import SignaturesFinder

debug = True


def test_simple_signature():
    s = converter.parse('tinyNotation: 4/4 C4 D E8 F C4 D E8 F C4 D E8 F')
    signatures = SignaturesFinder(score=s, threshold=0, benchmark_percent=100,
                                  min_note_count=4, max_note_count=4,
                                  min_signature_entries=3, max_signature_entries=100, show_logs=debug).run()
    if debug:
        print(*signatures)
    result = [*converter.parse('tinyNotation: 4/4 C4 D E8 F').flat.notes]
    if debug:
        print('Expected: ', result)
    assert signatures[0][0] == result

    s = converter.parse('tinyNotation: 4/4 C4 D E8 F C4 D E8 F C4 D E8 F C4 D E8 F')
    signatures = SignaturesFinder(score=s, threshold=0, benchmark_percent=100,
                                  min_note_count=4, max_note_count=4,
                                  min_signature_entries=4, max_signature_entries=100, show_logs=debug).run()
    if debug:
        print(*signatures)
    result = [*converter.parse('tinyNotation: 4/4 C4 D E8 F').flat.notes]
    if debug:
        print('Expected: ', result)
    assert signatures[0][0] == result


def test_mozart_signature():
    s = converter.parse(
        'https://kern.humdrum.org/cgi-bin/ksdata?location=users/craig/classical/mozart/piano/sonata&file=sonata10-2.krn&format=kern&o=norep'
    )
    signatures = SignaturesFinder(score=s, threshold=0, benchmark_percent=100,
                                  min_note_count=8, max_note_count=8,
                                  min_signature_entries=6, max_signature_entries=6, use_rhythmic=True, show_logs=debug).run()
    expected_result = [*converter.parse("tinyNotation: 3/4 d'16 c' b a a4 gn8 c'16. g32").flat.notes]
    if debug:
        print('Expected: ', expected_result)
    assert signatures_contain_expected_result(expected_result, signatures)

    s = converter.parse(
        'https://kern.humdrum.org/cgi-bin/ksdata?location=users/craig/classical/mozart/piano/sonata&file=sonata03-2.krn&format=kern'
    )
    signatures = SignaturesFinder(score=s, threshold=0, benchmark_percent=100,
                                  min_note_count=6, max_note_count=6,
                                  min_signature_entries=2, max_signature_entries=1000, use_rhythmic=True, show_logs=debug).run()
    expected_result = [*converter.parse("tinyNotation: 3/8 d'n32 c' b a g4 f#4").flat.notes]
    if debug:
        print('Expected: ', expected_result)
    assert signatures_contain_expected_result(expected_result, signatures)


def signatures_contain_expected_result(result, signatures):
    contains = False
    for i in range(0, len(signatures)):
        signature = signatures[i]
        print(*signature)
        for notes in signature:
            if len(notes) == len(result) and not contains:
                matching = True
                for j in range(0, len(notes)):
                    expected_note = result[j]
                    got_note = notes[j]
                    if got_note.pitch != expected_note.pitch and got_note.duration != expected_note.duration:
                        matching = False
                        break
                if matching:
                    if debug:
                        print('Got: ', *notes)
                    contains = True
                    break
        if contains:
            break
    return contains

# test_simple_signature()
test_mozart_signature()
#converter.parse("tinyNotation: 3/8 d'n32 c' b a g4 f#4").show()
