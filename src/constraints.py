from music21 import *
from music_converter import chromosome_to_midi
from collections import Counter

ALLOWED_TRIADS = [
    [0,2,4],
    [1,3,5],
    [2,4,6],
    [0,3,5],
    [1,4,6],
    [0,2,5],
    [1,3,6]
]
RANGES = [(53, 74), (48, 69), (41, 62)]
# F - d1 -> bas
# c - a1 -> tenor
# f - d2 -> alt

CHORD_FREQUENCY = {
    1: [(0, 1), (3, 1), (4, 1)],
    2: [(0, 2), (3, 2), (4, 2), (5, 1), (1, 2), (0, 3)],
    3: [(3, 3), (4, 3), (1, 1)],
    4: [(1, 3), (6, 2)],
    5: [(2, 1), (2, 2), (2, 3), (5, 2), (5, 3), (6, 1), (6, 3)]
}

def check_voice_range(chromosome: list, key: key.Key):
    if len(chromosome[0]) != 3:
        raise ValueError(f"Expected moment of length 3, got {len(chromosome[0])}")

    score = 0
    for moment in chromosome:
        for i, tone in enumerate(moment):
            curr_midi = chromosome_to_midi(tone, key)
            if curr_midi > RANGES[i][1]:
                score -= (curr_midi - RANGES[i][1])
            elif curr_midi < RANGES[i][0]:
                score -= (RANGES[i][0] - curr_midi)

    return score / len(chromosome)

def check_voice_crossing(chromosome: list):
    if len(chromosome[0]) != 4:
        raise ValueError(f"Expected moment of length 4, got {len(chromosome[0])}")
    
    penalty = 4
    score = 0

    for moment in chromosome:
        for i, note in enumerate(moment[:-1]):
            if note[0] < moment[i+1][0]:
                score -= penalty
            elif note[0] == moment[i+1][0]:
                if note[1] < moment[i+1][1]:
                    score -= penalty


    return score / len(chromosome)

def check_voice_overlap(chromosome: list):
    if len(chromosome[0]) != 4:
        raise ValueError(f"Expected moment of length 4, got {len(chromosome[0])}")
    
    penalty = 3
    score = 0

    for i, moment in enumerate(chromosome[:-1]):
        next_moment = chromosome[i+1]
        for j, (tone, alteration) in enumerate(moment[:-1]):
            next_tone, next_alteration = next_moment[j+1]
            if tone < next_tone:
                score -= penalty
            elif tone == next_tone:
                if alteration < next_alteration:
                    score -= penalty

        for j, (tone, alteration) in enumerate(moment[1:]):
            next_tone, next_alteration = next_moment[j]
            if tone > next_tone:
                score -= penalty
            elif tone == next_tone:
                if alteration > next_alteration:
                    score -= penalty

    return score / len(chromosome)

def check_monotone_motion(chromosome: list):
    if len(chromosome[0]) != 4:
        raise ValueError(f"Expected moment of length 4, got {len(chromosome[0])}")
    
    penalty = 2
    score = 0
    for i, curr in enumerate(chromosome[1:]):
        prev = chromosome[i]
        # ekstrakt tonova
        prev_tones = [t[0] for t in prev]
        curr_tones = [t[0] for t in curr]

        if all(tone1 < tone2 for tone1, tone2 in zip(prev_tones, curr_tones)):
            score -= penalty
        elif all(tone1 > tone2 for tone1, tone2 in zip(prev_tones, curr_tones)):
            score -= penalty

    return score / len(chromosome)

def check_voice_spacing(chromosome: list):
    if len(chromosome[0]) != 4:
        raise ValueError(f"Expected moment of length 4, got {len(chromosome[0])}")
    
    penalty = 3
    score = 0
    for moment in chromosome:
        for i, tone in enumerate(moment[:-2]):
            if tone[0] - moment[i+1][0] > 7:
                score -= penalty

        if moment[2][0] - moment[3][0] > 14:
            score -= penalty

    return score / len(chromosome)

def check_parallel_intervals(chromosome: list):
    if len(chromosome[0]) != 4:
        raise ValueError(f"Expected moment of length 4, got {len(chromosome[0])}")
    
    penalty = 4
    score = 0
    for i, moment in enumerate(chromosome[:-1]):
        for j, voice in enumerate(moment[:-1]):
            next_moment = chromosome[i + 1]

            curr_tone_up = voice[0]
            curr_tone_down = moment[j + 1][0]
            next_tone_up = next_moment[j][0]
            next_tone_down = next_moment[j + 1][0]

            interval_current = abs(curr_tone_up - curr_tone_down)
            interval_next = abs(next_tone_up - next_tone_down)

            if interval_current == interval_next and (interval_current == 4 or interval_current == 7):
                score -= penalty

    return score / len(chromosome)

def check_if_chords_exist(chromosome: list, is_minor: bool):
    if len(chromosome[0]) != 4:
        raise ValueError(f"Expected moment of length 4, got {len(chromosome[0])}")
    
    reward = 20
    penalty = 30
    score = 0
    chords = []
    
    for moment in chromosome:
        tones = [get_tone(tone)[0] for tone in moment]

        tones.sort()
        tones_set = list(set(tones))
        tones_set.sort()

        if tones_set in ALLOWED_TRIADS:
            chord = identify_chord(tones_set, moment, is_minor)
            chords.append(chord)
            if chord is not None:
                score += reward
        else:
            score -= penalty
            chords.append(None)

    return score / len(chromosome), chords

def check_starting_chord(starting_chord: list):
    if starting_chord == (0, 1):
        return 8
    elif starting_chord == (3, 1) or starting_chord == (4, 1):
        return 6
    
    return -10

def check_final_cadence(chords: list):
    if len(chords) < 4:
        return 0

    score = 0
    reward = 8
    penelty = 10

    if chords[-1] == (0, 1):
        score += reward
    else:
        score -= penelty

    if chords[-2] == (4, 1):
        score += 6
        if chords[-3] == (3, 1) or chords[-3] == (1, 2):
            score += 2
        elif chords[-3] == (0, 3):
            score += 2
            if chords[-4] == (1, 2) or chords[-4] == (3, 1):
                score += 1
    elif chords[-2] == (3, 1):
        score += 3

    return score

def check_function_transfer(chords: list, beat_strengths: list):
    score = 0
    penalty = 3

    for i, chord in enumerate(chords[:-1]):
        if beat_strengths[i] == 1 and beat_strengths[i+1] == 3 and \
        chord == chords[i+1]:
            score -= penalty

    return score / (len(chords) - 1)

def check_if_allowed_intervals(chromosome: list, key: key.Key):
    if len(chromosome[0]) != 3:
        raise ValueError(f"Expected moment of length 3, got {len(chromosome[0])}")
    
    score = 0
    penelty = 5

    for voice_index in range(3):
        for i in range(2):
            tone1 = chromosome[i][voice_index]
            tone2 = chromosome[i+1][voice_index]
            if not check_if_allowed_distance(tone1, tone2, key):
                score -= penelty
    return score / len(chromosome)

def check_if_violates_double_jump_dissonance(chromosome: list, key: key.Key):
    if len(chromosome[0]) != 3:
        raise ValueError(f"Expected moment of length 3, got {len(chromosome[0])}")
    
    score = 0
    penelty = 5

    for voice_index in range(3):
        for i,_ in enumerate(chromosome[:-2]):
            tone1 = chromosome[i][voice_index]
            tone2 = chromosome[i+1][voice_index]
            tone3 = chromosome[i+2][voice_index]
            if check_if_dissonance(tone1, tone2, tone3, key):
                score -= penelty
    return score / len(chromosome)

def check_forbidden_chord_progression(chords: list, beat_strengths: list):
    score = 0
    penalty = 5

    for i, chord1 in enumerate(chords[:-1]):
        chord2 = chords[i+1]
        if (chord1 == (4, 1) and chord2 == (3, 1)) or \
        (chord1 == (4, 2) and chord2 == (3, 1)) or \
        (chord1 == (5, 1) and chord2 == (0, 1)) or \
        (chord1 == (1, 1) and chord2 == (3, 1)) or \
        (chord1 == (4, 1) and chord2 == (1, 1)) or \
        (chord1 == (6, 1) and chord2 != (0, 1)) or \
        (chord1 == (0, 3) and chord2 != (4, 1)):
            score -= penalty
        elif chord1 == (0, 3) and chord2 == (4, 1) and (beat_strengths[i] == 1 or beat_strengths[i+1] > 1):
            score -= 2

    for i, chord1 in enumerate(chords[:-2]):
        chord2 = chords[i+1]
        chord3 = chords[i+2]
        if chord1 == (4, 1) and chord2 == (1, 1) and chord3 == (4, 1):
            score += penalty

    return score / len(chords)

def check_if_right_fifth_sixth_tone_progression(chords: list, chromosome: list):
    if len(chromosome[0]) != 4:
        raise ValueError(f"Expected moment of length 4, got {len(chromosome[0])}")
    
    score = 0
    reward = 5
    penalty = 4   

    for i, chord1 in enumerate(chords[:-1]):
        chord2 = chords[i+1]

        if (chord1 == (4, 1) and chord2 == (5, 1)) or \
        (chord1 == (5, 1) and chord2 == (4, 1)):
            idx = i if chord1 == (5, 1) else i+1

            if is_the_third_repeated(chromosome[idx], 5):
                score += reward
            else:
                score -= penalty

    return score / len(chords)

def check_chord_frequency(chords: list):
    score = 0
    for chord in chords:
        if chord is None:
            continue

        for freq_rank, chord_list in CHORD_FREQUENCY.items():
            if chord in chord_list:
                bonus = 2 ** (6 - freq_rank)
                if bonus > 10:
                    bonus = 10
                score += int(bonus)
                break
    return score / len(chords)

def identify_chord(chord: list, moment: list, is_minor: bool):
    if not verify_triad(moment, is_minor):
        return None

    return get_chord_info(moment, chord)


def is_the_third_repeated(moment: list, chord_idx: int):
    third_idx = get_third_index(chord_idx)
    third_num = ALLOWED_TRIADS[chord_idx][third_idx]

    count = sum(1 for note in moment if note[0] == third_num)

    return count == 2


#papir
def verify_triad(moment: list, is_minor: bool):
    steps_acc = [get_tone(t) for t in moment] 
    
    for tone, alteration in steps_acc:
        if tone == 6:
            if is_minor and alteration != 1:
                return False
            elif not is_minor and alteration != 0:
                return False
        else:
            if alteration != 0:
                return False
            
    tones = [get_tone(tone)[0] for tone in moment]
    tones_set = sorted(set(tones))
    
    chord_idx = ALLOWED_TRIADS.index(tones_set)
    
    counts = Counter(tones)
    repeated_tones = [t for t, c in counts.items() if c == 2]
    if len(repeated_tones) != 1:
        return False
    if any(c > 2 for c in counts.values()):
        return False

    repeated_tone = repeated_tones[0]
    triad_step = get_triad_tone(repeated_tone, chord_idx)

    bass_tone = get_tone(moment[3])[0]
    bass_step = get_triad_tone(bass_tone, chord_idx)

    if bass_step == 1:
        if chord_idx in [0, 3, 4]:
            if triad_step not in [1, 5]:
                return False
        elif chord_idx in [1, 2, 5]:
            if triad_step not in [1, 3]:
                return False
        else: #sedmi
            if triad_step != 3:
                return False
    elif bass_step == 3:
        if chord_idx in [0, 3, 4]:
            if triad_step not in [1, 5]:
                return False
        elif chord_idx in [2, 5]:
            if triad_step != 3:
                return False
        elif chord_idx == 6:
            if triad_step not in [3, 5]:
                return False
    else:
        if chord_idx in [0, 3, 4]:
            if triad_step not in [1, 5]:
                return False
        else:
            if triad_step != 3:
                return False

    return True
            
def get_tone(tone: list):
    return [tone[0] % 7, tone[1]]

def get_third_index(num: int):
    if num <= 2:
        return 1
    elif 3 <= num <= 4:
        return 2
    else:  # 5 <= idx <= 6
        return 0
    
def get_triad_tone(tone: int, chord_idx: int):
    chord = ALLOWED_TRIADS[chord_idx]
    third_idx = get_third_index(chord_idx)

    if tone == chord[third_idx]:
        return 3
    elif tone == chord[(third_idx + 1) % 3]:
        return 5
    elif tone == chord[(third_idx - 1) % 3]:
        return 1
    
def get_chord_info(moment: list, chord: list):
    chord_idx = ALLOWED_TRIADS.index(chord)
    bass = get_tone(moment[3])[0]
    bass_step = get_triad_tone(bass, chord_idx)

    if bass_step == 1:
        variation = 1
    elif bass_step == 3:
        variation = 2
    else:
        variation = 3
    return chord_idx, variation

def check_if_allowed_distance(tone1: list, tone2: list, key: key.Key):
    t1, t2 = tone1[0], tone2[0]
    t1_midi, t2_midi = chromosome_to_midi(tone1, key), chromosome_to_midi(tone2, key)
    midi_difference = abs(t1_midi - t2_midi)
    note_difference = abs(t1 - t2)

    if (midi_difference == 6 and note_difference == 3) or \
    (midi_difference == 8 and note_difference == 4) or \
    (midi_difference == 3 and note_difference == 1):
        return False

    return True

def check_if_dissonance(tone1: list, tone2: list, tone3: list, key: key.Key):
    t1, t2, t3 = tone1[0], tone2[0], tone3[0]
    t1_midi = chromosome_to_midi(tone1, key)
    t2_midi = chromosome_to_midi(tone2, key)
    t3_midi = chromosome_to_midi(tone3, key)

    midi_difference12 = abs(t1_midi - t2_midi)
    midi_difference23 = abs(t2_midi - t3_midi)

    note_difference12 = abs(t1 - t2)
    note_difference23 = abs(t2 - t3)
    note_difference13 = abs(t1 - t3)

    if (note_difference12 == 2 and note_difference23 == 2 and note_difference13 == 4 and \
        midi_difference12 == 4 and midi_difference23 == 4) or \
        (note_difference12 == 3 and note_difference23 == 3 and note_difference13 == 6 and \
        midi_difference12 == 5 and midi_difference23 == 5) or \
        (note_difference12 == 4 and note_difference23 == 4 and note_difference13 == 8 and \
        midi_difference12 == 7 and midi_difference23 == 7):
        return True
    
    return False