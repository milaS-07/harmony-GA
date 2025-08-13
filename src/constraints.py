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
