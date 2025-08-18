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

    return score

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


    return score

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
                # print(3)
                # print(i, moment)
                # print(tone, next_tone)
                score -= penalty
            elif tone == next_tone:
                if alteration > next_alteration:
                    # print(4)
                    # print(i, moment)
                    # print(tone, next_tone)
                    score -= penalty

    return score

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

    return score

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

    return score

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

    return score

def check_if_chords_exist(chromosome: list, is_minor: bool):
    if len(chromosome[0]) != 4:
        raise ValueError(f"Expected moment of length 4, got {len(chromosome[0])}")
    
    reward = 10
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
            chords.append(None)

    return score, chords


def identify_chord(chord: list, moment: list, is_minor: bool):
    if not verify_triad(moment, is_minor):
        return None

    return get_chord_info(moment, chord)

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
