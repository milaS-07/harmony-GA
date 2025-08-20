from constraints import *
from music_converter import combine_voices

func_map = {
    0: "I",
    1: "II",
    2: "III",
    3: "IV",
    4: "V",
    5: "VI",
    6: "VII",
}

inversion_map = {
    1: "",
    2: "6",
    3: "64"
}

def get_population_fitness(population: list, soprano: list, key: key.Key, beat_strengths: list):
    return [get_individual_fitness(ind, soprano, key, beat_strengths) for ind in population]

def get_individual_fitness(individual: list, soprano: list, key: key.Key, beat_strengths: list):
    fitness = 0

    voices_combined = combine_voices(soprano, individual)

    is_minor = key.mode == 'minor'

    fitness += check_voice_range(individual, key)
    fitness += check_voice_crossing(voices_combined)
    fitness += check_voice_overlap(voices_combined)
    fitness += check_monotone_motion(voices_combined)
    fitness += check_voice_spacing(voices_combined)
    fitness += check_parallel_intervals(voices_combined)
    
    score, chords = check_if_chords_exist(voices_combined, is_minor)
    fitness += score

    fitness += check_starting_chord(chords[0])
    fitness += check_function_transfer(chords, beat_strengths)
    fitness += check_final_cadence(chords)
    fitness += check_if_allowed_intervals(individual, key)
    fitness += check_if_violates_double_jump_dissonance(individual, key)
    fitness += check_forbidden_chord_progression(chords, beat_strengths)
    fitness += check_if_right_fifth_sixth_tone_progression(chords, voices_combined)
    fitness += check_chord_frequency(chords)

    formated = ", ".join(
        f"{func_map[chord[0]]}{inversion_map[chord[1]]}" if chord is not None else "None"
        for chord in chords
    )

    print(formated)

    return fitness