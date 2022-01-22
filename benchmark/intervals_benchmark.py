from music21.interval import Interval
from music21.note import Note

from benchmark.benchmark_utils import test_correctness


def get_intervals(notes):
    intervals = []
    for i in range(0, len(notes) - 1):
        note1 = notes[i]
        note2 = notes[i + 1]
        intervals.append(Interval(note1, note2))
    return intervals


def interval_benchmark(notes1, notes2):
    intervals1 = get_intervals(notes1)
    intervals2 = get_intervals(notes2)
    #print('First intervals: ', intervals1)
    #print('Second intervals: ', intervals2)
    return test_correctness(intervals1, intervals2)


 #notes1 = [Note('C4'), Note('G4'), Note('D4'), Note('D4'), Note('D5'), Note('D3')]
#notes2 = [Note('C4'), Note('G3'), Note('D4'), Note('D4'), Note('D5'), Note('D3')]
# print(interval_benchmark(notes1, notes2))
