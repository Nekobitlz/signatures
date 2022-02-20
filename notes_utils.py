from music21 import interval, pitch


def transpose_to_c(score):
    k = score.analyze('key')
    i = interval.Interval(k.tonic, pitch.Pitch('C'))
    return score.transpose(i)
