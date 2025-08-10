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
        for n in part.flatten().notesAndRests:
            n.expressions = []
            beat = n.beat
            if int(beat) == beat:
                if n.isNote:
                    new_note = note.Note(n.pitch)
                elif n.isRest:
                    new_note = note.Rest()
                else:
                    continue
                new_note.duration = n.duration
                clean_part.append(new_note)
                previous_note = new_note
            else:
                if previous_note is not None:
                    previous_note.duration.quarterLength += n.duration.quarterLength

        
        last_offset = 0
        for el in clean_part.notesAndRests:
            offset_end = el.offset + el.duration.quarterLength
            if offset_end > last_offset:
                last_offset = offset_end

        clean_part.duration = duration.Duration(last_offset)

        clean_score.append(clean_part)

    max_duration = max(part.duration.quarterLength for part in clean_score.parts)
    clean_score.duration = duration.Duration(max_duration)

    return clean_score

def get_soprano(score: stream.Score):
    return score.parts[0]

