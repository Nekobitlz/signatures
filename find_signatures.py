import random
from datetime import datetime

from music21 import *
from music21.chord import Chord
from music21.note import Note
from music21.stream import Stream, Part, Measure

from benchmark.signature_benchmark import SignatureBenchmark
from notes_utils import *

# score1 = converter.parse('http://kern.ccarh.org/cgi-bin/ksdata?l=users/craig/classical/bach/cello&file=bwv1007-01.krn&f=kern')
# score1 = converter.parse('https://kern.humdrum.org/cgi-bin/ksdata?location=users/craig/classical/mozart/piano/sonata&file=sonata15-1.krn&format=kern')
score1 = converter.parse('https://kern.humdrum.org/cgi-bin/ksdata?location=users/craig/classical/bach/371chorales&file=chor279.krn&f=kern')


# score1 = converter.parse('https://kern.humdrum.org/cgi-bin/ksdata?l=users/craig/classical/mozart/piano/sonata&file=sonata10-1.krn&f=kern&o=norep')
# score1 = converter.parse('https://kern.humdrum.org/cgi-bin/ksdata?location=users/craig/classical/chopin/prelude&file=prelude28-06.krn&format=kern')
# score1.show()

# todo фильтровать одинаковые сигнатуры - придумать как группировать одинаковые, привести сигнатуру к одному виду
# сделать через threshold, выбор эталона который будет наиболее похожим на все остальные, возможно > 1
# todo обработать разные части


class Signature:

    def __init__(self, notes, index):
        self.notes = notes
        self.index = index

    def __eq__(self, o: object):
        if isinstance(o, Signature):
            return self.notes == o.notes and self.index == o.index
        else:
            return super().__eq__(o)

    def __str__(self):
        return self.get_note_str()

    def __repr__(self):
        return self.get_note_str()

    def get_note_str(self):
        return ', '.join(str(n) for n in self.notes) + ' with index [' + ', '.join(str(n) for n in self.index) + ']'


class SignatureEntry:

    def __init__(self, signatures):
        self.signatures = signatures

    def __str__(self):
        return self.get_note_str()

    def __repr__(self):
        return self.get_note_str()

    def __eq__(self, o: object):
        if isinstance(o, SignatureEntry):
            return self.signatures[0] == o.signatures[0]
        else:
            return super().__eq__(o)

    def get_note_str(self):
        return 'Found signature with: ' + ', '.join(str(n) for n in self.signatures)


class SignaturesFinder:

    def __init__(self,
                 score=score1,
                 threshold=30,
                 benchmark_percent=60,
                 min_note_count=4,
                 max_note_count=10,
                 min_signature_entries=2,
                 max_signature_entries=10,
                 show_logs=True,
                 write_logs_in_file=False,
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
        self.logs_file = None
        if write_logs_in_file:
            self.logs_file = open('logs-' + datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), "w+")
        # искать ритмические сигнатуры
        self.use_rhythmic = use_rhythmic
        self.transposed_score = transpose_to_c(self.score)

    def __find_signatures__(self):
        benchmark = SignatureBenchmark(self.benchmark_percent, self.threshold, self.use_rhythmic, self.show_logs)
        intervals1 = self.__get_notes__(self.transposed_score)
        intervals2 = self.__get_notes__(self.transposed_score)
        notes_to_signature = {}
        result = []

        if len(intervals1) < len(intervals2):
            temp_interval = intervals1
            intervals1 = intervals2
            intervals2 = temp_interval

        for i in range(0, len(intervals1)):
            for k in range(i + self.min_note_count, len(intervals2)):
                j = i + self.min_note_count
                m = k + self.min_note_count
                signature = None
                while j <= i + self.max_note_count and k + self.max_note_count >= m and j <= k:
                    if 0 <= j <= len(intervals1) and 0 <= m <= len(intervals2):
                        notes1 = intervals1[i: j]
                        notes2 = intervals2[k: m]
                        key = create_key(notes1, notes2)
                        if key in notes_to_signature:
                            is_signature = notes_to_signature[key]
                        else:
                            is_signature = benchmark.is_signature(notes1, notes2)
                            notes_to_signature[key] = is_signature
                        if is_signature:
                            signature = SignatureEntry([Signature(notes1, [i, j]), Signature(notes2, [k, m])])
                    j += 1
                    m += 1
                if signature is not None:
                    result.append(signature)
                    self.__log__(str(signature))
        return result

    def __get_notes__(self, score):
        notes = []
        parts = self.__pick_notes_from_score__(score)
        for note in parts[0]:
            if isinstance(note, Note):
                notes.append(note)
            elif isinstance(note, Chord):
                notes.append(Note(note.root()))
            else:
                print('Unknown type: {}'.format(note))
        return notes

    @staticmethod
    def __pick_notes_from_score__(score):
        if isinstance(score, Part):
            parts = [score.flat.notes.stream()]
        elif isinstance(score, Measure):
            parts = [score.flat.notes.stream()]
        else:
            parts = [p.flat.notes.stream() for p in score.parts]
        return parts

    @staticmethod
    def __count_entries__(list):
        list_with_count, counted_elements = [], []
        for element in list:
            repeat_count = 0
            for counted_element in counted_elements:
                has_notes = False
                for signature in element.signatures:
                    if signature in counted_element.signatures:
                        has_notes = True
                        repeat_count += 1
                    elif has_notes:
                        counted_element.signatures.append(signature)
            if repeat_count <= 0:
                counted_elements = counted_elements + [element]
        for element in counted_elements:
            list_with_count = list_with_count + [[element, len(element.signatures)]]
        return list_with_count

    def __filter_signatures_by_entries(self, list_with_count):
        result = []
        for index in range(0, len(list_with_count)):
            element = list_with_count[index]
            if self.min_signature_entries <= element[1] <= self.max_signature_entries:
                result.append(element[0])
        return result

    def highlight_signatures(self, filtered_signatures):
        notes = self.__pick_notes_from_score__(self.transposed_score)[0]
        for signatureEntry in filtered_signatures:
            color = '#' + ''.join(random.sample('0123456789ABCDEF', 6))
            for signature in signatureEntry.signatures:
                for i in range(signature.index[0], signature.index[1]):
                    notes[i].style.color = color
        self.transposed_score.show()

    def run(self):
        self.__log__('Started signature search for ' + str(self.score))
        start_time = datetime.now()
        signature_entries = self.__find_signatures__()
        end_time = datetime.now()

        self.__log__('Time: ' + str(end_time - start_time))
        self.__log__('Founded signature entries len: ' + str(len(signature_entries)))

        counted_entries = self.__count_entries__(signature_entries)
        self.__log__('Counted entries len: ' + str(len(counted_entries)))

        filtered_signatures = self.__filter_signatures_by_entries(counted_entries)
        self.__log__('Filtered signatures by entries: ' + str(len(filtered_signatures)))

        self.highlight_signatures(filtered_signatures)
        result = []
        for entries in filtered_signatures:
            unique_notes = []
            for signature in entries.signatures:
                if signature.notes not in unique_notes:
                    unique_notes.append(signature.notes)
            result.append(unique_notes)
        if self.logs_file is not None:
            self.logs_file.close()
        return result

    def __log__(self, str):
        if self.show_logs:
            print(str)
        if self.logs_file is not None:
            self.logs_file.write(str + "\n")
