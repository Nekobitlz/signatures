from music21 import interval, pitch


def transpose_to_c(score):
    k = score.analyze('key')
    i = interval.Interval(k.tonic, pitch.Pitch('C'))
    return score.transpose(i)


def notes_to_str(notes):
    return ','.join([str(note.pitch) for note in notes])


def create_key(notes1, notes2):
    str1 = notes_to_str(notes1)
    str2 = notes_to_str(notes2)
    return str1 + ' ' + str2


def create_pair_key(notes1, notes2):
    key_str = ""
    if len(notes1) != len(notes2):
        return key_str
    for i in range(0, len(notes1)):
        key_str += create_note_pair(notes1[i], notes2[i])
        if i < len(notes1) - 1:
            key_str += " "
    return key_str


def create_note_pair(note1, note2):
    return str(note1.pitch) + ',' + str(note2.pitch)
