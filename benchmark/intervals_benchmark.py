from music21.interval import Interval

from benchmark.benchmark_utils import test_correctness


def get_intervals(notes):
    intervals = []
    for i in range(0, len(notes) - 1):
        note1 = notes[i]
        note2 = notes[i + 1]
        interval = Interval(note1, note2).semitones
        intervals.append(interval)
    return intervals


def interval_benchmark(notes1, notes2):
    intervals1 = get_intervals(notes1)
    intervals2 = get_intervals(notes2)
    return test_correctness(intervals1, intervals2)
