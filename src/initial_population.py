from collections import Counter
import random
from music21 import *
from music_converter import midi_to_chromosome, chromosome_to_midi
from constraints import RANGES, ALLOWED_TRIADS, get_tone, verify_triad
import itertools


def generate_initial_population(soprano: list, key: key.Key, num_population: int):
    population = []
    
    for i in range(num_population):
        population.append(generate_individual(soprano, key))

    return population

def generate_individual(soprano: list, key: key.Key):
    individual = []
    for i in range(len(soprano)):
        moment = []
        soprano_midi = chromosome_to_midi(soprano[i], key)

        upper_limit = soprano_midi

        for j, (low, high) in enumerate(RANGES):
            voice_high = min(high, upper_limit)
            voice_low = low

            down_chrom = midi_to_chromosome(voice_low, key)[0]
            up_chrom = midi_to_chromosome(voice_high, key)[0]

            alteration = 0

            while True:
                if down_chrom >= up_chrom:
                    upper_limit = chromosome_to_midi([down_chrom, alteration], key)

                    moment.append([down_chrom, alteration])
                    break

                tone = random.randint(down_chrom, up_chrom)

                if right_voice_ranges(tone, alteration, upper_limit, key) and \
                    (random.random() < 0.2 or right_voice_spacing(moment, tone, soprano[i]))  and \
                    (random.random() < 0.02 or check_if_triad(soprano[i], moment + [[tone, alteration]], key)) and \
                    (i == 0 or no_voice_overlap(tone, alteration, individual[i-1], j + 1, i, soprano)):
                        upper_limit = chromosome_to_midi([tone, alteration], key)

                        moment.append([tone, alteration])
                        break


        individual.append(moment)

    return individual

def right_voice_ranges(tone: int, alteration: int, upper_limit: int, key: key.Key):
    return chromosome_to_midi([tone, alteration], key) <= upper_limit

def no_voice_overlap(tone: int, alteration: int, last_moment: list, voice_ind: int, moment_ind: int, soprano: list): #TODO da nikad ne gresi
    whole_last_moment = [soprano[moment_ind - 1]]
    whole_last_moment.extend(last_moment)

    last_moment_tone_up = whole_last_moment[voice_ind - 1][0]
    last_moment_alteration_up = whole_last_moment[voice_ind - 1][1]

    if voice_ind == 3:
        if tone > last_moment_tone_up:
            return False
        elif tone == last_moment_tone_up:
            return alteration <= last_moment_alteration_up
        else:
            return True
    else:
        last_moment_tone_down = whole_last_moment[voice_ind + 1][0]
        last_moment_alteration_down = whole_last_moment[voice_ind + 1][1]

        if last_moment_tone_down < tone < last_moment_tone_up:
            return True
        elif last_moment_tone_down == tone:
            return last_moment_alteration_down <= alteration
        elif tone == last_moment_tone_up:
            return last_moment_alteration_up >= alteration
        else:
            return False

def right_voice_spacing(moment: list, tone: int, soprano_moment: list):
    moment_length = len(moment)
    if moment_length == 3:
        if moment[2][0] - tone > 14:
            return False
    elif moment_length == 2:
        if moment[0][0] - tone > 7:
            return False
    else:
        if soprano_moment[0] - tone > 7:
            return False
        
    return True

def check_if_triad(soprano_moment: list, current_moment: list, key: key.Key):
    possible_chords = ALLOWED_TRIADS.copy()

    current_notes = [soprano_moment[0]] + [note[0] for note in current_moment]
    current_notes = [get_tone([n, 0])[0] for n in current_notes]

    is_minor = key.mode == 'minor'

    counts = Counter(current_notes)
    repeated_tones = [t for t, c in counts.items() if c > 1]


    if len(current_notes) == 4:
        if len(repeated_tones) != 1 or any(c > 2 for c in counts.values()):
            return False #or not i == len(current_notes) - 1
        
        unique_notes = sorted(set(current_notes))
        if unique_notes not in ALLOWED_TRIADS:
            return False
        
        moment_for_verify = [[n, 0] for n in current_notes]
        return verify_triad(moment_for_verify, is_minor)

    counts = Counter(current_notes)
    repeated_tones = [t for t, c in counts.items() if c > 1]
    if len(repeated_tones) > 1 or any(c > 2 for c in counts.values()):
        return False


    to_continue = False
    current_notes_temp = current_notes[:-1]
    for triad in ALLOWED_TRIADS:
        if not set(current_notes_temp).issubset(triad):
            continue
        for combo in itertools.product(triad, repeat=(4 - len(current_notes_temp))):
            full_moment = current_notes_temp + list(combo)
            if len(set(full_moment)) != 3:
                continue
            moment_for_verify = [[n, 0] for n in full_moment]
            if verify_triad(moment_for_verify, is_minor):
                to_continue = True
                break

    if not to_continue:
        return True

    for triad in ALLOWED_TRIADS:
        if not set(current_notes).issubset(triad):
            continue
        for combo in itertools.product(triad, repeat=(4 - len(current_notes))):
            full_moment = current_notes + list(combo)
            if len(set(full_moment)) != 3:
                continue
            moment_for_verify = [[n, 0] for n in full_moment]
            if verify_triad(moment_for_verify, is_minor):
                return True


    return False
    