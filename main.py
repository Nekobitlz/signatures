import music21
from music21 import *

# music21.configure.run()
from music21.chord import Chord
from music21.note import Note
from music21.pitch import Pitch

n = note.Note("D#3")
n.duration.type = 'half'
# n.show()

littleMelody = converter.parse("tinynotation: 3/4 c4 d8 f g16 a g f#")
# littleMelody.show()

dicant = corpus.parse('trecento/Fava_Dicant_nunc_iudei')
# dicant.plot('histogram', 'pitch')

score1 = converter.parse('http://kern.ccarh.org/cgi-bin/ksdata?l=users/craig/classical/bach/cello&file=bwv1007-01.krn&f=kern')
score2 = converter.parse('https://kern.humdrum.org/cgi-bin/ksdata?location=users/craig/classical/bach/371chorales&file=chor279.krn&f=kern')
# score2.show()

notes_threshold = 1
interval_size = 4


# length_piece = int(score1.asTimespans()[-1].offset)


def find_same_intervals():
    intervals1 = get_notes(score1)
    intervals2 = get_notes(score2)
    result = []

    if len(intervals1) < len(intervals2):
        temp_interval = intervals1
        intervals1 = intervals2
        intervals2 = temp_interval

    for i in range(0, len(intervals1)):
        for k in range(0, len(intervals2)):
            precision = 0
            j = i
            m = k
            while precision <= notes_threshold and j <= i + interval_size and m <= k + interval_size:
                if 0 <= j < len(intervals1) and 0 <= m < len(intervals2):
                    if intervals1[j] != intervals2[m]:
                        precision += 1
                    j += 1
                    m += 1
                else:
                    precision = notes_threshold + 1
                    break
            if precision <= notes_threshold:
                result.append(intervals2[k: m - 1])
    return result


def get_notes(score):
    intervals = []
    parts = [p.flat.notesAndRests.stream() for p in score.parts]
    for part in parts:
        for note in part:
            if isinstance(note, Note):
                # print(note.pitch)
                intervals.append(note.pitch)
            elif isinstance(note, Chord):
                chord = list(map(lambda x: x.pitch, note.notes))
                # print('Chord: {}'.format(chord))
                intervals.append(chord)
            else:
                print('Unknown type: {}'.format(note))
    return intervals


# посмотреть разные части
# only add notes that are long enough

print(find_same_intervals())
