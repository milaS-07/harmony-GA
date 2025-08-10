from music21 import *
from score_utils import *

def soprano_to_chromosom(soprano: stream.Score):
    chromosom = []

    detected_key = soprano.analyze('key') #TODO dodatak da se smanji greska

    tonic = get_tonic_pitch(detected_key)
    
    for note in soprano.flatten().notes:
        current_pitch = note.pitch 
        chromosom.append(tone_to_chromosom(current_pitch, detected_key, tonic))


    return chromosom


def tone_to_chromosom(note_obj, key: key.Key, tonic: pitch.Pitch):
    #print(f"tone_to_chromosom: primljen element tipa {type(note_obj)}, sadržaj: {note_obj}")
    if isinstance(note_obj, note.Rest):
        #print("tone_to_chromosom: Pauza detektovana, vraćam None")
        return None
    
    tone = note_obj.pitch

    scale = key.getScale()


    notes_order = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

    tonic_letter = tonic.name[0].upper()
    tone_letter = tone.name[0].upper()
    distance = (notes_order.index(tone_letter) - notes_order.index(tonic_letter)) % 7

    first_num = distance + (tone.octave - tonic.octave) * 7

    if notes_order.index(tonic_letter) > notes_order.index(tone_letter):
        first_num -= 7


    if scale.getScaleDegreeFromPitch(tone) is not None:
        second_num = 0
    else:
        pitch_up = pitch.Pitch(tone.name)
        pitch_down = pitch.Pitch(tone.name)

        alter = tone.accidental.alter if tone.accidental else 0

        pitch_up.accidental = pitch.Accidental(alter - 1)
        pitch_down.accidental = pitch.Accidental(alter + 1)

        if scale.getScaleDegreeFromPitch(pitch_up) is not None:
            second_num = 1
        elif scale.getScaleDegreeFromPitch(pitch_down) is not None:
            second_num = -1
        else:
            return 0
    

    return [first_num, second_num]


def get_tonic_pitch(key_signature: key.Key):
    tonic_pitch = key_signature.tonic


    letter = tonic_pitch.name[0].upper()
    octave = 0

    if letter in ['C', 'D', 'E', 'F']:
        octave = 4
    elif letter in ['G', 'A', 'B']:
        octave = 3
    
    tonic_pitch.octave = octave
    return tonic_pitch


def score_to_chromosom(score):
    parts = list(score.parts)[:4]
    seqs = [list(p.flatten().notesAndRests) for p in parts]

    indices = [0, 0, 0, 0]
    remaining = []

    for v in range(4):
        if len(seqs[v]) > 0:
            remaining.append(seqs[v][0].quarterLength)
        else:
            remaining.append(float('inf'))

    detected_key = score.analyze('key')
    tonic = get_tonic_pitch(detected_key)

    chromosom = []

    while any(indices[v] < len(seqs[v]) for v in range(4)):
        active = [remaining[v] for v in range(4) if indices[v] < len(seqs[v])]
        if not active:
            break
        min_len = min(active)

        moment = []

        all_rests = True
        for v in range(4):
            if indices[v] >= len(seqs[v]):
                continue
            el = seqs[v][indices[v]]
            if not isinstance(el, note.Rest):
                all_rests = False


        if all_rests:
            for v in range(4):
                if indices[v] < len(seqs[v]):
                    remaining[v] -= min_len
                    if remaining[v] <= 1e-9:
                        indices[v] += 1
                        if indices[v] < len(seqs[v]):
                            remaining[v] = seqs[v][indices[v]].quarterLength
                        else:
                            remaining[v] = float('inf')
            continue

        for v in range(4):
            if indices[v] >= len(seqs[v]):
                moment.append(None)
                continue
            el = seqs[v][indices[v]]
            moment.append(tone_to_chromosom(el, detected_key, tonic))

        chromosom.append(moment)

        for v in range(4):
            if indices[v] >= len(seqs[v]):
                continue
            remaining[v] -= min_len
            if remaining[v] <= 1e-9:
                indices[v] += 1
                if indices[v] < len(seqs[v]):
                    remaining[v] = seqs[v][indices[v]].quarterLength
                else:
                    remaining[v] = float('inf')

    return chromosom





broj = 13
korpus_cist = get_bach_corpus(broj)

korpus = get_clean_harmony(korpus_cist)

# sopran = get_soprano(korpus)

# #print(soprano_to_chromosom(sopran))
# print(soprano_to_chromosom(korpus))


aligned = score_to_chromosom(korpus)
print(aligned)



korpus.show()