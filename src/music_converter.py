from music21 import *
from score_utils import *

def soprano_to_chromosom(soprano: stream.Score):
    chromosom = []

    detected_key = soprano.analyze('key')

    tonic = get_tonic_pitch(detected_key)
    
    for note in soprano.flatten().notes:
        current_pitch = note.pitch 
        chromosom.append(tone_to_chromosom(current_pitch, detected_key, tonic))


    return chromosom




def tone_to_chromosom(tone: pitch.Pitch, key: key.Key, tonic: pitch.Pitch):
    scale = key.getScale()


    notes_order = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

    tonic_letter = tonic.name[0].upper()
    tone_letter = tone.name[0].upper()
    distance = (notes_order.index(tone_letter) - notes_order.index(tonic_letter)) % 7

    first_num = distance + (tone.octave - tonic.octave) * 7

    if notes_order.index(tonic_letter) > notes_order.index(tone_letter):
        first_num -= 7

    #print(f"distance: {distance}, tone: {tone.octave}, tonic: {tonic.octave}")

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



p = pitch.Pitch('B3')
k = key.Key('D', 'minor')
#k = key.Key('D')

s = k.getScale()

#print(noteToChromosom(n, k))
#print(s.getScaleDegreeFromPitch(n))
#print(tone_to_chromosom(p, k))

korpus = get_clean_harmony(get_bach_corpus(1))
sopran = get_soprano(korpus)

print(soprano_to_chromosom(sopran))

korpus.show()