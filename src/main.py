import random
import time
import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from music_converter import *
from initial_population import *
from score_utils import *
from fitness import *
from selection import *
from crossover import *
from mutation import *

from music21 import corpus

OUTPUT_DIR = "results"
LOG_DIR = "logs"

def run_experiment(melody_id, num_rules, run_idx, pop_size, num_gens, save_results, save_logs):
    if str(melody_id).endswith(('.mxl', '.xml', '.musicxml')):
        folder_id = os.path.splitext(os.path.basename(str(melody_id)))[0]
    else:
        folder_id = str(melody_id)

    run_dir = os.path.join(OUTPUT_DIR, f"rules{num_rules}", f"melody{folder_id}", f"run{run_idx}")
    
    if save_results and os.path.exists(run_dir):
        print(f"[SKIP] Melody {melody_id}, Rules {num_rules}, Run {run_idx} već postoji")
        return
    
    if save_results:
        os.makedirs(run_dir, exist_ok=True)

    if str(melody_id).endswith(('.mxl', '.xml', '.musicxml')):
        from music21 import converter
        korpus = converter.parse(str(melody_id))
        try:
            sopran = get_soprano(korpus)
        except:
            sopran = korpus
    elif any(c.isalpha() for c in str(melody_id)):
        from music21 import stream, note
        sopran = stream.Part()
        for n_str in str(melody_id).split():
            try:
                sopran.append(note.Note(n_str))
            except:
                pass
    else:
        korpus_cist = get_bach_corpus(int(melody_id))
        korpus = get_clean_harmony(korpus_cist)
        sopran = get_soprano(korpus)

    sopran_chrom = soprano_to_chromosome(sopran)

    beat_strengths = get_beat_strengths(sopran)
    detected_key = sopran.analyze('key')

    if save_logs:
        set_log_context(num_rules, melody_id, run_idx)

    # Generisanje početne populacije
    t0 = time.perf_counter()
    population = generate_initial_population(sopran_chrom, detected_key, pop_size)
    t1 = time.perf_counter()
    init_time = t1 - t0

    # Evolucija
    fitness_history = []
    t2 = time.perf_counter()
    for gen_idx in range(num_gens):
        fitnesses = get_population_fitness(
            population, sopran_chrom, detected_key, beat_strengths,
            generation_idx=gen_idx, num_rules=num_rules, save_logs=save_logs
        )
        fitness_history.append(fitnesses)

        if gen_idx < num_gens - 1:
            population = select_new_population(population, fitnesses)
            population = do_crossover(population)
            population = mutate_population(population, sopran_chrom, detected_key)
            
    t3 = time.perf_counter()
    evol_time = t3 - t2
    total_time = init_time + evol_time

    # --- Najbolja jedinka ---
    final_fitnesses = get_population_fitness(
        population, sopran_chrom, detected_key, beat_strengths,
        generation_idx=num_gens - 1, num_rules=num_rules, save_logs=False
    )
    population = select_new_population(population, final_fitnesses)
    
    best_individual = population[0]
    best_score = build_full_score(sopran, best_individual, detected_key)

    # --- Čuvanje rezultata ---
    if save_results:
        fitness_file = os.path.join(run_dir, "fitness.txt")
        with open(fitness_file, "w") as f:
            for gen in fitness_history:
                f.write(",".join(str(round(x, 2)) for x in gen) + "\n")

        # Vreme izvršavanja
        time_file = os.path.join(run_dir, "time.txt")
        with open(time_file, "w") as f:
            f.write(f"init_time={init_time:.4f}\n")
            f.write(f"evol_time={evol_time:.4f}\n")
            f.write(f"total_time={total_time:.4f}\n")

        # Najbolja jedinka (MusicXML)
        xml_file = os.path.join(run_dir, "best.musicxml")
        best_score.write("musicxml", fp=xml_file)
        
    return sopran, population, detected_key


def run_single(melody_id, num_rules, pop_size, num_gens, save_results, save_logs):
    if save_results:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
    if save_logs:
        set_log_context(num_rules, melody_id, run_idx=1)

    if str(melody_id).endswith(('.mxl', '.xml', '.musicxml')):
        from music21 import converter, stream, note, meter, key
        korpus = converter.parse(str(melody_id))
        
        sopran = stream.Part()
        sopran.id = 'soprano'
        
        for el in korpus.recurse().notesAndRests:
            if el.isNote:
                n = note.Note(el.pitch)
                n.quarterLength = el.quarterLength
                sopran.append(n)
            elif el.isRest:
                r = note.Rest()
                r.quarterLength = el.quarterLength
                sopran.append(r)
                
        ts = korpus.recurse().getElementsByClass(meter.TimeSignature)
        if ts: 
            sopran.insert(0, ts[0])
        ks = korpus.recurse().getElementsByClass(key.KeySignature)
        if ks: 
            sopran.insert(0, ks[0])
            
    elif any(c.isalpha() for c in str(melody_id)):
        from music21 import stream, note
        sopran = stream.Part()
        sopran.id = 'soprano'
        for n_str in str(melody_id).split():
            try:
                sopran.append(note.Note(n_str))
            except:
                pass
    else:
        korpus_cist = get_bach_corpus(int(melody_id))
        korpus = get_clean_harmony(korpus_cist)
        sopran = get_soprano(korpus)

    sopran_chrom = soprano_to_chromosome(sopran)
    beat_strengths = get_beat_strengths(sopran)
    
    potrebna_duzina = len(sopran_chrom) + 1
    if len(beat_strengths) < potrebna_duzina:
        poslednji_element = beat_strengths[-1] if beat_strengths else 1
        while len(beat_strengths) < potrebna_duzina:
            beat_strengths.append(poslednji_element)

    detected_key = sopran.analyze('key')
    
    # Prva generacija
    population = generate_initial_population(sopran_chrom, detected_key, pop_size)
    fitnesses = get_population_fitness(population, sopran_chrom, detected_key, beat_strengths, 0, num_rules, save_logs)
    print("Inicijalni fitness:", [round(f, 1) for f in fitnesses])
    print("---")

    # Sledeće generacije
    for gen_idx in range(1, num_gens - 1):
        fitnesses = get_population_fitness(population, sopran_chrom, detected_key, beat_strengths, gen_idx, num_rules, save_logs)
        population = select_new_population(population, fitnesses)
        
        fitnesses_after_selection = get_population_fitness(population, sopran_chrom, detected_key, beat_strengths, gen_idx, num_rules, False)
        print(f"Gen {gen_idx} nakon selekcije:", [round(f, 1) for f in fitnesses_after_selection])
        print("---")
        
        # NAPOMENA: Uklonjen random.shuffle da ne bi uništio elitizam i redosled nakon selekcije
        population = do_crossover(population)
        population = mutate_population(population, sopran_chrom, detected_key)

    # Poslednja generacija
    print("Kraj evolucije, procesuiranje poslednje generacije...")
    fitnesses = get_population_fitness(population, sopran_chrom, detected_key, beat_strengths, num_gens - 1, num_rules, save_logs)
    population = select_new_population(population, fitnesses)
    print("~~~")
    fitnesses_after_selection = get_population_fitness(population, sopran_chrom, detected_key, beat_strengths, num_gens - 1, num_rules, False)
    print("Finalni fitness:", [round(f, 1) for f in fitnesses_after_selection])
    
    best_individual = population[0]
    best_fitness_generated = build_full_score(sopran, best_individual, detected_key)
    
    if save_results:
        if str(melody_id).endswith(('.mxl', '.xml', '.musicxml')):
            display_name = os.path.splitext(os.path.basename(str(melody_id)))[0]
        elif any(c.isalpha() for c in str(melody_id)):
            display_name = "custom"
        else:
            display_name = str(melody_id)
        run_dir = os.path.join(OUTPUT_DIR, f"rules{num_rules}_melody_{display_name}")
        os.makedirs(run_dir, exist_ok=True)
        best_fitness_generated.write("musicxml", fp=os.path.join(run_dir, "best.musicxml"))
        
    best_fitness_generated.show()


class HarmonyGAApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Konfiguracija GA Eksperimenta")
        self.root.geometry("480x650")
        
        self.var_results = tk.BooleanVar(value=False)
        self.var_logs = tk.BooleanVar(value=False)
        self.var_mode = tk.StringVar(value="single")
        self.var_source_type = tk.StringVar(value="corpus")
        self.selected_file_path = ""

        self.create_widgets()
        self.toggle_mode()

    def create_widgets(self):
        frame_files = ttk.LabelFrame(self.root, text=" Izlazni Fajlovi ", padding=10)
        frame_files.pack(fill="x", padx=15, pady=5)
        
        ttk.Checkbutton(frame_files, text="Generiši 'results' fajlove", variable=self.var_results).pack(anchor="w")
        ttk.Checkbutton(frame_files, text="Generiši 'log' (JSON) fajlove", variable=self.var_logs).pack(anchor="w")

        frame_mode = ttk.LabelFrame(self.root, text=" Režim rada ", padding=10)
        frame_mode.pack(fill="x", padx=15, pady=5)
        
        ttk.Radiobutton(frame_mode, text="Pojedinačno izvršavanje", variable=self.var_mode, value="single", command=self.toggle_mode).pack(anchor="w")
        ttk.Radiobutton(frame_mode, text="Više izvršavanja", variable=self.var_mode, value="multi", command=self.toggle_mode).pack(anchor="w")

        frame_params = ttk.LabelFrame(self.root, text=" Osnovni Parametri ", padding=10)
        frame_params.pack(fill="x", padx=15, pady=5)
        
        ttk.Label(frame_params, text="Broj generacija:").grid(row=0, column=0, sticky="w", pady=2)
        self.ent_gens = ttk.Entry(frame_params, width=10)
        self.ent_gens.insert(0, "20")
        self.ent_gens.grid(row=0, column=1, sticky="w", pady=2, padx=5)

        ttk.Label(frame_params, text="Veličina populacije:").grid(row=1, column=0, sticky="w", pady=2)
        self.ent_pop = ttk.Entry(frame_params, width=10)
        self.ent_pop.insert(0, "20")
        self.ent_pop.grid(row=1, column=1, sticky="w", pady=2, padx=5)

        self.frame_dynamic = ttk.LabelFrame(self.root, text="Podešavanje primera ", padding=10)
        self.frame_dynamic.pack(fill="both", expand=True, padx=15, pady=5)

        self.btn_run = ttk.Button(self.root, text="POKRENI", command=self.execute_program)
        self.btn_run.pack(fill="x", padx=15, pady=15)

    def toggle_mode(self):
        for widget in self.frame_dynamic.winfo_children():
            widget.destroy()

        if self.var_mode.get() == "single":
            self.ent_gens.delete(0, tk.END)
            self.ent_gens.insert(0, "20")
            self.ent_pop.delete(0, tk.END)
            self.ent_pop.insert(0, "20")

            frame_src_select = ttk.Frame(self.frame_dynamic)
            frame_src_select.pack(fill="x", pady=2)
            
            ttk.Radiobutton(frame_src_select, text="Korpus ID", variable=self.var_source_type, value="corpus", command=self.update_source_inputs).grid(row=0, column=0, padx=5)
            ttk.Radiobutton(frame_src_select, text="Uvezi MXL", variable=self.var_source_type, value="file", command=self.update_source_inputs).grid(row=0, column=1, padx=5)
            ttk.Radiobutton(frame_src_select, text="Ručni unos", variable=self.var_source_type, value="custom", command=self.update_source_inputs).grid(row=0, column=2, padx=5)

            self.frame_input_container = ttk.Frame(self.frame_dynamic)
            self.frame_input_container.pack(fill="x", pady=5)
            
            self.update_source_inputs()

            ttk.Label(self.frame_dynamic, text="Broj pravila:").pack(anchor="w", pady=2)
            self.cb_single_rules = ttk.Combobox(self.frame_dynamic, values=[5, 8, 10, 15], state="readonly", width=12)
            self.cb_single_rules.set(15)
            self.cb_single_rules.pack(anchor="w", pady=2)
            
        else:
            self.ent_gens.delete(0, tk.END)
            self.ent_gens.insert(0, "300")
            self.ent_pop.delete(0, tk.END)
            self.ent_pop.insert(0, "300")

            ttk.Label(self.frame_dynamic, text="Izaberite skupove pravila:").pack(anchor="w")
            self.lb_rules = tk.Listbox(self.frame_dynamic, selectmode="multiple", height=4, exportselection=0)
            for r in [5, 8, 10, 15]:
                self.lb_rules.insert(tk.END, r)
            self.lb_rules.select_set(0, tk.END)
            self.lb_rules.pack(fill="x", pady=2)

            ttk.Label(self.frame_dynamic, text="Unesite ID-eve melodija (odvojeni zarezom):").pack(anchor="w")
            self.ent_multi_melodies = ttk.Entry(self.frame_dynamic)
            self.ent_multi_melodies.insert(0, "5, 227, 54, 213")
            self.ent_multi_melodies.pack(fill="x", pady=2)

            ttk.Label(self.frame_dynamic, text="Broj izvršavanja za svaku kombinaciju:").pack(anchor="w")
            self.ent_runs = ttk.Entry(self.frame_dynamic, width=10)
            self.ent_runs.insert(0, "20")
            self.ent_runs.pack(anchor="w", pady=2)

    def update_source_inputs(self):
        for widget in self.frame_input_container.winfo_children():
            widget.destroy()
            
        stype = self.var_source_type.get()
        if stype == "corpus":
            ttk.Label(self.frame_input_container, text="ID melodije 2-371 (npr. 107, 227):").pack(anchor="w", pady=2)
            self.ent_single_melody = ttk.Entry(self.frame_input_container, width=15)
            self.ent_single_melody.insert(0, "107")
            self.ent_single_melody.pack(anchor="w", pady=2)
        elif stype == "file":
            ttk.Label(self.frame_input_container, text="Izaberite fajl (.mxl):").pack(anchor="w", pady=2)
            row = ttk.Frame(self.frame_input_container)
            row.pack(fill="x")
            self.lbl_file_info = ttk.Label(row, text="Nijedan fajl nije izabran", width=25)
            self.lbl_file_info.pack(side="left", padx=2)
            def browse():
                fp = filedialog.askopenfilename(filetypes=[("MusicXML", "*.mxl *.xml *.musicxml")])
                if fp:
                    self.selected_file_path = fp
                    self.lbl_file_info.config(text=os.path.basename(fp))
            ttk.Button(row, text="Pretraži...", command=browse).pack(side="left", padx=2)
        elif stype == "custom":
            ttk.Label(self.frame_input_container, text="Unesite note (npr. C4 D#4 Eb4 ...):").pack(anchor="w", pady=2)
            self.ent_custom_melody = ttk.Entry(self.frame_input_container, width=35)
            self.ent_custom_melody.insert(0, "C4 D4 E4 D4 C4")
            self.ent_custom_melody.pack(anchor="w", pady=2)

    def execute_program(self):
        try:
            pop_size = int(self.ent_pop.get())
            num_gens = int(self.ent_gens.get())
        except ValueError:
            messagebox.showerror("Greška", "Veličina populacije i broj generacija moraju biti celi brojevi.")
            return

        save_results = self.var_results.get()
        save_logs = self.var_logs.get()

        if save_logs:
            if os.path.exists(LOG_DIR):
                shutil.rmtree(LOG_DIR)
            os.makedirs(LOG_DIR, exist_ok=True)
            
        if save_results:
            os.makedirs(OUTPUT_DIR, exist_ok=True)

        if self.var_mode.get() == "single":
            stype = self.var_source_type.get()
            if stype == "corpus":
                melody_id = self.ent_single_melody.get().strip()
                if not melody_id:
                    messagebox.showerror("Greška", "Unesite ID melodije.")
                    return
            elif stype == "file":
                if not self.selected_file_path:
                    messagebox.showerror("Greška", "Izaberite fajl preko pretrage.")
                    return
                melody_id = self.selected_file_path
            else:
                melody_id = self.ent_custom_melody.get().strip()
                if not melody_id:
                    messagebox.showerror("Greška", "Unesite note za melodiju.")
                    return

            try:
                num_rules = int(self.cb_single_rules.get())
            except ValueError:
                messagebox.showerror("Greška", "Izaberite ispravan broj pravila.")
                return
            
            print(f"\n[START] Pojedinačno izvršavanje: Melodija {melody_id}, Pravila {num_rules}")
            self.root.destroy()
            run_single(melody_id, num_rules, pop_size, num_gens, save_results, save_logs)

        else:
            selected_rule_indices = self.lb_rules.curselection()
            if not selected_rule_indices:
                messagebox.showerror("Greška", "Morate izabrati bar jedan skup pravila.")
                return
            rule_sets = [self.lb_rules.get(i) for i in selected_rule_indices]

            try:
                melody_ids = [x.strip() for x in self.ent_multi_melodies.get().split(",") if x.strip()]
                num_runs = int(self.ent_runs.get())
            except ValueError:
                messagebox.showerror("Greška", "Proverite unos za melodije i broj izvršavanja.")
                return

            print(f"\n[START] Eksperiment: Pravila {rule_sets}, Melodije {melody_ids}, Izvršavanja {num_runs}")
            self.root.destroy()

            for num_rules in rule_sets:
                for melody_id in melody_ids:
                    for run_idx in range(1, num_runs + 1):
                        print(f"=== Melody {melody_id}, Rules {num_rules}, Run {run_idx} ===")
                        run_experiment(melody_id, num_rules, run_idx, pop_size, num_gens, save_results, save_logs)
            print("\n[KRAJ] Svi primeri su uspešno izvršeni.")


def main():
    root = tk.Tk()
    HarmonyGAApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()