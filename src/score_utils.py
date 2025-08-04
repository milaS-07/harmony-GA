from music21 import *

def get_bach_corpus(corpus_num: int):
    for i, score in enumerate(corpus.chorales.Iterator()):
        if i == corpus_num:
            return score

def get_clean_harmony(score: stream.Score):
    clean_score = stream.Score()
    voice_names = ['soprano', 'alto', 'tenor', 'bass']

    detected_key = score.analyze('key')
    key_signature = key.KeySignature(detected_key.sharps)

    for i, part in enumerate(score.parts[:4]):
        clean_part = stream.Part()
        clean_part.id = voice_names[i]

        clean_part.append(key_signature)

        previous_note = None
        for n in part.flat.notes:
            n.expressions = []

            beat = n.beat
            if int(beat) == beat:
                new_note = note.Note(n.pitch)
                new_note.duration = n.duration
                clean_part.append(new_note)
                previous_note = new_note
            else:
                if previous_note is not None:
                    previous_note.duration.quarterLength += n.duration.quarterLength

        clean_score.append(clean_part)

    clean_score.makeMeasures(inPlace=True)
    return clean_score

def get_soprano(score: stream.Score):
    return score.parts[0]


score = get_bach_corpus(9)

#score.show()
get_clean_harmony(score).show()

#get_soprano(score).show()
#get_soprano(get_clean_harmony(score).show()

