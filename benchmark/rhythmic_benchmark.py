from music21.note import Note

from benchmark.benchmark_utils import test_correctness


def get_durations(notes):
    durations = []
    for i in range(0, len(notes)):
        note: Note = notes[i]
        durations.append(note.duration)
    return durations


def rhythmic_benchmark(notes1, notes2):
    durations1 = get_durations(notes1)
    durations2 = get_durations(notes2)
    return test_correctness(durations1, durations2)
