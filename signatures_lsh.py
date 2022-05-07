from datetime import datetime

from music21 import converter
from music21.chord import Chord
from music21.interval import Interval
from music21.note import Note
from music21.stream import Part, Measure

from lsh import LSH
from notes_utils import transpose_to_c, to_hash

# score1 = converter.parse('https://kern.humdrum.org/cgi-bin/ksdata?location=users/craig/classical/bach/371chorales&file=chor279.krn&f=kern')
score1 = converter.parse('tinyNotation: 4/4 C4 D E8 F C4 D E8 F C4 D E8 F C4 D E8 F')
# score1 = converter.parse(
#    'https://kern.humdrum.org/cgi-bin/ksdata?location=users/craig/classical/mozart/piano/sonata&file=sonata10-2.krn&format=kern&o=norep')


class SignaturesFinder:

    def __init__(self,
                 score=score1,
                 threshold=30,
                 benchmark_percent=60,
                 min_note_count=4,
                 max_note_count=10,
                 min_signature_entries=4,
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
        self.min_note_count = min_note_count - 1
        # максимальное количество нот, при котором последовательность считается сигнатурой
        self.max_note_count = max_note_count - 1
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
        self.transposed_notes = []

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
    def __map_notes__(notes, use_rhythmic):
        digits = []
        for i in range(0, len(notes) - 1):
            note1: Note = notes[i]
            note2: Note = notes[i + 1]
            interval = Interval(note1, note2).semitones
            if use_rhythmic:
                durations = note2.duration.ordinal - note1.duration.ordinal
                digits.append(to_hash(interval, durations))
            else:
                digits.append(interval)
        return digits

    @staticmethod
    # create K-shingles by sliding window approach
    def getShingles(notes, K=3):
        d1 = []
        for i in range(len(notes) - K + 1):
            elemt = notes[i:i + K]
            d1.append(elemt)
        print(f"Found {len(d1)} unique shingles, out of {len(notes)} possible.")
        return d1

    def run(self):
        self.transposed_notes = self.__get_notes__(self.transposed_score)
        notes = self.__map_notes__(self.transposed_notes, self.use_rhythmic)
        signatures = self.getShingles(notes, self.min_note_count)
        print(signatures)

        lsh = LSH(1)

        for signature in signatures:
            lsh.add_hash(signature)

        print(lsh.buckets)

        candidate_pairs = lsh.check_candidates(self.min_signature_entries, self.max_signature_entries)
        print(len(candidate_pairs))
        print(list(candidate_pairs))

        result = []
        for candidate in candidate_pairs:
            current_signature = []
            for el in candidate:
                current_notes = []
                if el == 114 or el == 380:
                    stop = True
                for i in range(el, el + self.min_note_count + 1):
                    current_notes.append(self.transposed_notes[i])
                current_signature.append(current_notes)
            result.append(current_signature)

        return result

        # doc_shingles = [self.getShingles(notes, c) for c in range(self.min_note_count, self.min_note_count)]


#SignaturesFinder().run()