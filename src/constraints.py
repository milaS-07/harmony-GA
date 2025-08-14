from music21 import *
from music_converter import chromosome_to_midi

ALLOWED_TRIPLES = [
    [0,2,4],
    [1,3,5],
    [2,4,6],
    [1,3,6],
    [2,4,7],
    [0,3,5],
    [1,4,6]
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
                score -= curr_midi - RANGES[i][1]
            elif curr_midi < RANGES[i][0]:
                score -= RANGES[i][0] - curr_midi

    return score

def check_voice_crossing(chromosome: list):
    if len(chromosome[0]) != 4:
        raise ValueError(f"Expected moment of length 4, got {len(chromosome[0])}")
    
    penalty = 5
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
    
    penalty = 5
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
    
    penalty = 3
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
    
    penalty = 4
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
    
    penalty = 5
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

def check_if_chords_exist(chromosome: list):
    if len(chromosome[0]) != 4:
        raise ValueError(f"Expected moment of length 4, got {len(chromosome[0])}")
    
    reward = 15
    score = 0
    for moment in chromosome:
        if check_if_chord(moment):
            score += reward

    return score



def get_tone(tone: list):
    return [tone[0] % 7, tone[1]]

def check_if_chord(moment: list):
    tones = [get_tone(tone)[0] for tone in moment]

    for x in set(tones):
        if tones.count(x) == 2:
            the_rest = [y for y in tones if y != x]
            if the_rest[0] != the_rest[1]:
                return check_if_triad(tones) #TODO kasnije dodati provere i za ostale akorde

    
    return False

def check_if_triad(tones: list):
    tones.sort()

    if tones[1] != tones[2]:
        the_rest = list(set(tones))
        the_rest.sort()

        return the_rest in ALLOWED_TRIPLES


    return False