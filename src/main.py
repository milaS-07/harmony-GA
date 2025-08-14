from music_converter import *
from initial_population import *
from score_utils import *
from constraints import * #TODO obrisati kasnije
from fitness import *
from selection import *

def main():
    broj = 13
    korpus_cist = get_bach_corpus(broj)

    korpus = get_clean_harmony(korpus_cist)

    sopran = get_soprano(korpus)
    sopran_chrom = soprano_to_chromosome(sopran)

    detected_key = sopran.analyze('key')
    
    ostali_glasovi = generate_initial_population(sopran_chrom, detected_key, 10)#[0]

    # sve = combine_voices(sopran_chrom, ostali_glasovi)


    # generisano = build_full_score(sopran, ostali_glasovi, detected_key)
    
    fitnesi = get_population_fitness(ostali_glasovi, sopran_chrom, detected_key)

    print(fitnesi)

    fitnesi_novi = get_population_fitness(select_new_population(ostali_glasovi, fitnesi), sopran_chrom, detected_key)

    print(fitnesi_novi)
    #generisano.show()

if __name__ == "__main__":
    main()