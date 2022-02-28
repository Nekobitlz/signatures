from datetime import datetime

from music21 import *
from music21.chord import Chord
from music21.note import Note
from music21.stream import Stream, Part, Measure

from benchmark.signature_benchmark import SignatureBenchmark
from notes_utils import transpose_to_c

# score1 = converter.parse('http://kern.ccarh.org/cgi-bin/ksdata?l=users/craig/classical/bach/cello&file=bwv1007-01.krn&f=kern')
# score1 = converter.parse('https://kern.humdrum.org/cgi-bin/ksdata?location=users/craig/classical/mozart/piano/sonata&file=sonata15-1.krn&format=kern')
score1 = converter.parse('https://kern.humdrum.org/cgi-bin/ksdata?location=users/craig/classical/bach/371chorales&file=chor279.krn&f=kern')
#score1 = converter.parse('https://kern.humdrum.org/cgi-bin/ksdata?l=users/craig/classical/mozart/piano/sonata&file=sonata10-1.krn&f=kern&o=norep')


# score1 = converter.parse('https://kern.humdrum.org/cgi-bin/ksdata?location=users/craig/classical/chopin/prelude&file=prelude28-06.krn&format=kern')
# score1.show()

# todo фильтровать одинаковые сигнатуры - придумать как группировать одинаковые, привести сигнатуру к одному виду
# сделать через threshold, выбор эталона который будет наиболее похожим на все остальные, возможно > 1
# todo обработать разные части
# todo брать сигнатуры и потом проходить по произведениям смотреть где она там
# todo отмечать сигнатуры в исходном произведении текстом или фоном

class IndexedNotes:

    def __init__(self, notes, indexes):
        self.notes = notes
        self.indexes = indexes

    def __eq__(self, o: object):
        if isinstance(o, IndexedNotes):
            return self.notes == o.notes and self.indexes == o.indexes
        else:
            return super().__eq__(o)


class Signature:

    def __init__(self, notes):
        self.notes = notes

    def __str__(self):
        return self.get_note_str()

    def __repr__(self):
        return self.get_note_str()

    def __eq__(self, o: object):
        return self.notes == o

    def get_note_str(self):
        return 'Found signature with: ' + ', '.join(str(n) for n in self.notes)


class SignaturesFinder:

    def __init__(self,
                 score=score1,
                 threshold=20,
                 benchmark_percent=80,
                 min_note_count=4,
                 max_note_count=10,
                 min_signature_entries=4,
                 max_signature_entries=10,
                 show_logs=True,
                 use_rhythmic=False):
        self.score = score
        # допустимый процент несовпадения
        self.threshold = threshold
        # контрольный показатель совпадения, при котором тест считается пройденным
        self.benchmark_percent = benchmark_percent
        # минимальное количество нот, при котором последовательность считается сигнатурой
        self.min_note_count = min_note_count
        # максимальное количество нот, при котором последовательность считается сигнатурой
        self.max_note_count = max_note_count
        # минимальное количество раз, которое сигнатура может встречаться в произведении
        self.min_signature_entries = min_signature_entries
        # максимальное количество раз, которое сигнатура может встречаться в произведении
        self.max_signature_entries = max_signature_entries
        # показывать ли дебажные логи
        self.show_logs = show_logs
        # искать ритмические сигнатуры
        self.use_rhythmic = use_rhythmic

    def __find_signatures(self):
        benchmark = SignatureBenchmark(self.benchmark_percent, self.threshold, self.use_rhythmic, self.show_logs)
        transposed_score = transpose_to_c(self.score)
        intervals1 = self.__get_notes(transposed_score)
        intervals2 = self.__get_notes(transposed_score)
        result = []

        if len(intervals1) < len(intervals2):
            temp_interval = intervals1
            intervals1 = intervals2
            intervals2 = temp_interval

        for i in range(0, len(intervals1)):
            for k in range(i + self.min_note_count, len(intervals2)):
                j = i + self.min_note_count
                m = k + self.min_note_count
                has_signature = False
                notes1 = []
                notes2 = []
                while j <= i + self.max_note_count and k + self.max_note_count >= m and j <= k:
                    if 0 <= j <= len(intervals1) and 0 <= m <= len(intervals2):
                        notes1 = intervals1[i: j]
                        notes2 = intervals2[k: m]
                        has_signature = benchmark.is_signature(notes1, notes2)
                    j += 1
                    m += 1
                if has_signature:
                    signature = Signature([notes1, notes2])
                    result.append(signature)
                    if self.show_logs:
                        print(signature)
        return result

    def __get_notes(self, score):
        notes = []
        if isinstance(score, Part):
            parts = [score.flat.notesAndRests.stream()]
        elif isinstance(score, Measure):
            parts = [score.flat.notesAndRests.stream()]
        else:
            parts = [p.flat.notesAndRests.stream() for p in score.parts]
        key = score.analyze('key')
        for note in parts[0]:
            if isinstance(note, Note):
                notes.append(note)
            elif isinstance(note, Chord):
                # trying to get leading tone from chord
                for chord_pitch in note.pitches:
                    if key.chord.pitches.__contains__(chord_pitch):
                        if self.show_logs:
                            print('Got note from chord: ', chord_pitch)
                        notes.append(Note(chord_pitch))
                        break

            else:
                print('Unknown type: {}'.format(note))
        return notes

    def __count_repeated(self, list):
        list_with_count, counted_elements = [], []
        for element in list:
            repeated = False
            for counted_element in counted_elements:
                has_notes = False
                for notes in element.notes:
                    if notes in counted_element.notes:
                        has_notes = True
                        repeated = True
                    elif has_notes:
                        counted_element.notes.append(notes)
            if repeated:
                for index in range(len(list_with_count)):
                    if list_with_count[index][0] == element:
                        list_with_count[index][1] = list_with_count[index][1] + 1
            else:
                counted_elements = counted_elements + [element]
                list_with_count = list_with_count + [[element, 1]]
        return list_with_count

    def __filter_signatures_by_entries(self, list_with_count):
        result = []
        for index in range(0, len(list_with_count)):
            element = list_with_count[index]
            if self.min_signature_entries <= element[1] <= self.max_signature_entries:
                result.append(element[0])
        return result

    def highlight_signatures(self, filtered_signatures):
        for note in self.score.flat.notes:
            for signature in filtered_signatures:
                for signature_note in signature.notes:
                    if note in signature_note:
                        note.style.color = 'red'
        self.score.show()

    def run(self):
        start_time = datetime.now()
        signatures = self.__find_signatures()
        end_time = datetime.now()
        print('Time: ', end_time - start_time)
        print('Founded signatures len: ', len(signatures))

        counted_signatures = self.__count_repeated(signatures)
        print('Counted signatures len: ', len(counted_signatures))

        filtered_signatures = self.__filter_signatures_by_entries(counted_signatures)
        print('Filtered signatures by entries: ', len(filtered_signatures))

        self.highlight_signatures(filtered_signatures)
        result = []
        for signature in filtered_signatures:
            result.append(signature.notes)
        return result

print(*SignaturesFinder().run(), sep='\n')

# K330
# Time:  0:39:25.342773
# Founded signatures len:  176454
# Counted signatures len:  1458
# Filtered signatures by entries:  249

# K332
# Time:  0:09:02.194635
# Founded signatures len:  89788
# Counted signatures len:  1046
# Filtered signatures by entries:  382
