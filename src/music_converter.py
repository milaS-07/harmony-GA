from music21 import *


def soprano_to_chromosome(soprano: stream.Score):
    chromosome = []

    detected_key = soprano.analyze('key') #TODO dodatak da se smanji greska

    tonic = get_tonic_pitch(detected_key)
    
    for note in soprano.flatten().notes:
        current_pitch = note.pitch 
        chromosome.append(tone_to_chromosome(current_pitch, detected_key, tonic))


    return chromosome

def tone_to_chromosome(note_obj, key: key.Key, tonic: pitch.Pitch):
    if isinstance(note_obj, note.Rest):
        return None
    
    if isinstance(note_obj, note.Note):
        tone = note_obj.pitch
    elif isinstance(note_obj, pitch.Pitch):
        tone = note_obj

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

def score_to_chromosome(score):
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

    chromosome = []

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
            moment.append(tone_to_chromosome(el, detected_key, tonic))

        chromosome.append(moment)

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

    return chromosome

def chromosome_to_midi(tone: list, key: key.Key):
    degree_offset, alteration = tone
    
    tonic_pitch = get_tonic_pitch(key)

    scale = key.getScale()
    target_pitch = scale.pitchFromDegree((degree_offset % 7) + 1)

    octave_shift = degree_offset // 7
    target_pitch.octave += octave_shift

    if tonic_pitch.octave == 3:
        target_pitch.octave -= 1

    target_pitch = target_pitch.transpose(alteration)

    return target_pitch.midi


def midi_to_chromosome(midi: int, key: key.Key):
    tonic_pitch = get_tonic_pitch(key)

    n = note.Note(midi)

    return tone_to_chromosome(n, key, tonic_pitch)

def combine_voices(soprano: list, three_voices: list):
    all = []
    for i in range(len(soprano)):
        new_list = [soprano[i]] + three_voices[i]
        all.append(new_list)
    return all

def chromosome_to_tone(chrom: list, key_signature: key.Key, tonic: pitch.Pitch):
    if chrom is None:
        return None

    notes_order = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    
    first_num, second_num = chrom
    
    tonic_idx = notes_order.index(tonic.name[0].upper())
    
    note_idx = (tonic_idx + first_num) % 7
    note_letter = notes_order[note_idx]
    
    octave_shift = (tonic_idx + first_num) // 7
    octave = tonic.octave + octave_shift
    
    base_pitch = pitch.Pitch()
    base_pitch.octave = octave
    base_pitch.name = note_letter

    scale = key_signature.getScale()

    p = pitch.Pitch(base_pitch.nameWithOctave)
    _, a = scale.getScaleDegreeAndAccidentalFromPitch(base_pitch)

    a_val = a.alter if a is not None else 0
    if a is not None:
        current_alter = p.accidental.alter if p.accidental else 0
        p.accidental = pitch.Accidental(current_alter - a_val)

    if second_num == 0:
        return p
    else:
        base_alter = p.accidental.alter if p.accidental is not None else 0

        new_alter = base_alter + second_num
        
        p.accidental = pitch.Accidental(new_alter)
        
        return p
    
def build_full_score(soprano_part: stream.Part, other_voices_chrom: list, key_signature: key.Key):
    tonic_pitch = get_tonic_pitch(key_signature)

    full_score = stream.Score()
    full_score.append(soprano_part)

    voice_names = ['alto', 'tenor', 'bass']
    other_parts = [stream.Part(id=voice_name) for voice_name in voice_names]

    for part in other_parts:
        part.append(key_signature)

    soprano_notes = list(soprano_part.notesAndRests)
    for i, sop_note in enumerate(soprano_notes):
        chroms = other_voices_chrom[i]

        for voice_idx in range(3):
            chrom = chroms[voice_idx]

            if isinstance(sop_note, note.Rest):
                new_note = note.Rest()
                new_note.duration = sop_note.duration
            else:
                new_pitch = chromosome_to_tone(chrom, key_signature, tonic_pitch)
                new_note = note.Note(new_pitch)
                new_note.duration = sop_note.duration

            other_parts[voice_idx].append(new_note)

    for part in other_parts:
        full_score.append(part)

    return full_score
    
