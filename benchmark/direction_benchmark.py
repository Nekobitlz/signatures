import enum

from music21.note import Note

from benchmark.benchmark_utils import test_correctness


class Direction(enum.Enum):
    up = 1
    down = 2
    same = 3


def get_directions(notes):
    notes_len = len(notes)
    directions = []
    for i in range(0, notes_len - 1):
        if i < i + 1 < notes_len:
            note1: Note = notes[i]
            note2: Note = notes[i + 1]
            if note1 == note2:
                directions.append(Direction.same)
            elif note1 < note2:
                directions.append(Direction.up)
            else:
                directions.append(Direction.down)
        else:
            break
    return directions


def direction_benchmark(notes1, notes2):
    directions1 = get_directions(notes1)
    directions2 = get_directions(notes2)
    return test_correctness(directions1, directions2)
