from music21 import converter

from find_signatures import SignaturesFinder


def test_simple_signature():
    s = converter.parse('tinyNotation: 4/4 C4 D E8 F C4 D E8 F C4 D E8 F')
    signatures = SignaturesFinder(score=s, threshold=0, benchmark_percent=100,
                                  min_note_count=4, max_note_count=4,
                                  min_signature_entries=3, max_signature_entries=100, show_logs=True).run()
    print(*signatures)
    result = [*converter.parse('tinyNotation: 4/4 C4 D E8 F').flat.notes]
    print('Expected: ', result)
    assert signatures[0][0] == result


test_simple_signature()
