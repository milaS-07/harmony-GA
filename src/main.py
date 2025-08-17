import random
from music_converter import *
from initial_population import *
from score_utils import *
from constraints import * #TODO obrisati kasnije
from fitness import *
from selection import *
from crossover import *
from mutation import *

def main():
    num_generation = 10
    population_size = 10

    broj = 5
    korpus_cist = get_bach_corpus(broj)

    korpus = get_clean_harmony(korpus_cist)

    sopran = get_soprano(korpus)
    sopran_chrom = soprano_to_chromosome(sopran)

    detected_key = sopran.analyze('key')
    
    population = generate_initial_population(sopran_chrom, detected_key, population_size)

    print(get_population_fitness(population, sopran_chrom, detected_key))
    print("---")

    for _ in range(num_generation - 1):
        fitnesses = get_population_fitness(population, sopran_chrom, detected_key)
        population = select_new_population(population, fitnesses)
        fitnesses_after_selection = get_population_fitness(population, sopran_chrom, detected_key)
        print(fitnesses_after_selection)
        print("---")
        random.shuffle(population)
        population = do_crossover(population)
        population = mutate_population(population, detected_key)

    print("kraj")
    fitnesses = get_population_fitness(population, sopran_chrom, detected_key)
    population = select_new_population(population, fitnesses)
    print("~~~")
    fitnesses_after_selection = get_population_fitness(population, sopran_chrom, detected_key)
    print(fitnesses_after_selection)


    best_fitness_genereted = build_full_score(sopran, population[0], detected_key)
    #best_fitness_genereted.show()

if __name__ == "__main__":
    main()