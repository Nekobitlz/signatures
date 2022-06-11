import json

from music21.note import Note


class NoteEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Note):
            note_fields = {"pitch": obj.nameWithOctave, 'duration': float(obj.quarterLength)}
            return note_fields
        return "empty"


def note_decoder(obj):
    if 'pitch' in obj and 'duration' in obj:
        return Note(nameWithOctave=obj['pitch'], quarterLength=obj['duration'])
    return obj
