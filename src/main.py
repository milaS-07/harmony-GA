from music_converter import *
from initial_population import *
from score_utils import *

def main():
    broj = 4
    korpus_cist = get_bach_corpus(broj)

    korpus = get_clean_harmony(korpus_cist)

    sopran = get_soprano(korpus)
    sopran_chrom = soprano_to_chromosom(sopran)

    detected_key = sopran.analyze('key')
    
    ostali_glasovi = generate_initial_population(sopran_chrom, detected_key)[0]

    sve = combine_voices(sopran_chrom, ostali_glasovi)

    generisano = build_full_score(sopran, ostali_glasovi, detected_key)

    # print(sopran_chrom)
    # print(ostali_glasovi)
    print(sve)

    generisano.show()

if __name__ == "__main__":
    main()