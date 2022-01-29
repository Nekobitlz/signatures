from datetime import datetime

from music21 import *
from music21.chord import Chord
from music21.note import Note
from music21.stream import Stream

from benchmark.signature_benchmark import SignatureBenchmark

score1 = converter.parse('http://kern.ccarh.org/cgi-bin/ksdata?l=users/craig/classical/bach/cello&file=bwv1007-01.krn&f=kern')
#score1 = converter.parse('https://kern.humdrum.org/cgi-bin/ksdata?location=users/craig/classical/bach/371chorales&file=chor279.krn&f=kern')
# score1.show()
# score2.show()

# todo методы скользящего окна
# todo фильтровать одинаковые сигнатуры - придумать как группировать одинаковые, привести сигнатуру к одному виду
# todo обработать разные части
# todo брать сигнатуры и потом проходить по произведениям смотреть где она там
# todo оценить в лучшем, худшем и в среднем

# CONTROLLERS REGION start



class Signature:

    def __init__(self, notes1, notes2):
        self.notes1 = notes1
        self.notes2 = notes2

    def __str__(self):
        return self.get_note_str()

    def __repr__(self):
        return self.get_note_str()

    def __eq__(self, o: object):
        return self.notes1 == o or self.notes2 == o

    def get_note_str(self):
        return 'Found signature with: ' + ', '.join(str(n) for n in self.notes1) + ' and ' + ', '.join(str(n) for n in self.notes2)


# допустимый процент несовпадения
threshold = 0
# контрольный показатель совпадения, при котором тест считается пройденным
benchmark_percent = 100
# минимальное количество нот, при котором последовательность считается сигнатурой
min_note_count = 4
# максимальное количество нот, при котором последовательность считается сигнатурой
max_note_count = 10
# минимальное количество раз, которое сигнатура может встречаться в произведении
min_signature_entries = 4
# максимальное количество раз, которое сигнатура может встречаться в произведении
max_signature_entries = 10
# показывать ли дебажные логи
show_logs = True
# искать ритмические сигнатуры
use_rhythmic = False

min_duration = 0.1


# CONTROLLERS REGION end


def find_signatures():
    intervals1 = get_notes(transpose_to_c(score1))
    intervals2 = get_notes(transpose_to_c(score1))
    result = []

    if len(intervals1) < len(intervals2):
        temp_interval = intervals1
        intervals1 = intervals2
        intervals2 = temp_interval

    for i in range(0, len(intervals1), max_note_count):
        if i + max_note_count < len(intervals2):
            search_index = i + max_note_count
        else:
            search_index = len(intervals2) - 1
        for k in range(search_index, len(intervals2), max_note_count):
            j = i + max_note_count
            m = k + max_note_count
            signature = []
            notes1 = []
            notes2 = []
            while j > i + min_note_count and m > k + min_note_count:
                if 0 <= j < len(intervals1) and 0 <= m < len(intervals2):
                    benchmark = SignatureBenchmark(benchmark_percent, threshold, use_rhythmic, show_logs)
                    notes1 = intervals1[i: j]
                    notes2 = intervals2[k: m]
                    if benchmark.is_signature(notes1, notes2):
                        signature = notes2
                        break
                j -= 1
                m -= 1
            if len(signature) > 0:
                result.append(Signature(notes1, notes2))
                if show_logs:
                    print('Found signature with: ', notes1, ' and ', notes2)
    return result


def get_notes(score):
    notes = []
    parts = [p.flat.notesAndRests.stream() for p in score.parts]
    key = score.analyze('key')
    for note in parts[0]:
        if isinstance(note, Note):
            notes.append(note)
        elif isinstance(note, Chord):
            # trying to get leading tone from chord
            for chord_pitch in note.pitches:
                if key.chord.pitches.__contains__(chord_pitch):
                    if show_logs:
                        print('Got note from chord: ', chord_pitch)
                    notes.append(chord_pitch)
                    break
        else:
            print('Unknown type: {}'.format(note))
    return notes


def count_repeated(list):
    list_with_count, counted_elements = [], []
    for element in list:
        if not (element in counted_elements):
            counted_elements = counted_elements + [element]
            list_with_count = list_with_count + [[element, 1]]
        else:
            for index in range(len(list_with_count)):
                if list_with_count[index][0] == element:
                    list_with_count[index][1] = list_with_count[index][1] + 1
    return list_with_count


def filter_signatures_by_entries(list_with_count):
    result = []
    for index in range(0, len(list_with_count)):
        element = list_with_count[index]
        if min_signature_entries <= element[1] <= max_signature_entries:
            result.append(element[0])
    return result


def transpose_to_c(score):
    k = score.analyze('key')
    i = interval.Interval(k.tonic, pitch.Pitch('C'))
    return score.transpose(i)


start_time = datetime.now()
signatures = find_signatures()
end_time = datetime.now()
print('Time: ', end_time - start_time)
print('Founded signatures len: ', len(signatures))

counted_signatures = count_repeated(signatures)
print('Counted signatures len: ', len(counted_signatures))

filtered_signatures = filter_signatures_by_entries(counted_signatures)
print('Filtered signatures by entries: ', len(filtered_signatures))
for element in filtered_signatures:
    stream1 = Stream()
    stream1.append(element.notes1)
    stream1.append(note.Rest())
    stream1.append(note.Rest())
    stream1.append(note.Rest())
    stream1.append(element.notes2)
    stream1.show()
print(*filtered_signatures, sep='\n')


# Founded signatures len:  316
# Counted signatures len:  61
# Filtered signatures by entries:  31