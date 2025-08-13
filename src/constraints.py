from music21 import *
from music_converter import chromosome_to_midi

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