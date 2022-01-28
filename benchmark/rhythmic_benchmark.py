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
   # print('First durations: ', durations1)
   # print('Second durations: ', durations2)
    return test_correctness(durations1, durations2)


notes1 = [Note('C4'), Note('G4'), Note('D4'), Note('D4'), Note('D5'), Note('D3')]
notes2 = [Note('C4'), Note('G3'), Note('D4'), Note('D4'), Note('D5'), Note('D3')]
#print(rhythmic_benchmark(notes1, notes2))