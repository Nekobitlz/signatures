from itertools import groupby

from music21 import *
from music21.interval import Interval

score1 = converter.parse('http://kern.ccarh.org/cgi-bin/ksdata?l=users/craig/classical/bach/cello&file=bwv1007-01.krn&f=kern')
score2 = converter.parse('https://kern.humdrum.org/cgi-bin/ksdata?location=users/craig/classical/bach/371chorales&file=chor279.krn&f=kern')
#score1.show()
#score2.show()

intervals_threshold = 0
interval_size = 4
min_duration = 0.1


# length_piece = int(score1.asTimespans()[-1].offset)


class NoteInterval:

    def __init__(self, notes, interval_between):
        self.notes = notes
        self.interval = interval_between

    def __str__(self):
        return self.get_note_str() + " - " + self.interval.niceName

    def __repr__(self):
        return self.get_note_str() + " - " + self.interval.niceName

    def get_note_str(self):
        return ', '.join(str(n) for n in self.notes)


def find_same_intervals():
    intervals1 = get_intervals(score1)
    intervals2 = get_intervals(score2)
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
            while precision <= intervals_threshold and j <= i + interval_size and m <= k + interval_size:
                if 0 <= j < len(intervals1) and 0 <= m < len(intervals2):
                    if intervals1[j].interval != intervals2[m].interval:
                        precision += 1
                    j += 1
                    m += 1
                else:
                    precision = intervals_threshold + 1
                    break
            if precision <= intervals_threshold:
                result.append(intervals2[k: m - 1])
    return result


def get_intervals(score):
    intervals = []
    parts = [p.flat.notesAndRests.stream() for p in score.parts]
    for part in parts:
        for i in range(0, len(part) - 1):
            note1 = part[i]
            note2 = part[i + 1]
            current_interval = Interval(note1, note2)
            intervals.append(NoteInterval([note1, note2], current_interval))

   # print(intervals)
    return intervals


print(*[el for el, _ in groupby(find_same_intervals())], sep='\n')
