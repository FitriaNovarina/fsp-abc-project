import numpy as np
import random
import copy

def calculate_makespan(sequence, df):
    """Menghitung total waktu pengerjaan (makespan) menggunakan logika Flow-Shop"""
    num_jobs = len(sequence)
    num_stages = len(df.columns) - 1
    
    C = np.zeros((num_jobs, num_stages))
    
    for i in range(num_jobs):
        job_idx = df['Projek'].tolist().index(sequence[i])
        for j in range(num_stages):
            time = df.iloc[job_idx, j+1]
            if i == 0 and j == 0:
                C[i][j] = time
            elif i == 0:
                C[i][j] = C[i][j-1] + time
            elif j == 0:
                C[i][j] = C[i-1][j] + time
            else:
                C[i][j] = max(C[i-1][j], C[i][j-1]) + time
                
    return C[-1][-1]

def get_fitness(sequence, df):
    """Rumus fitness = 1 / Makespan"""
    makespan = calculate_makespan(sequence, df)
    if makespan == 0: return 0
    return 1.0 / makespan

def swap_operator(seq):
    s = list(seq)
    i1, i2 = random.sample(range(len(s)), 2)
    s[i1], s[i2] = s[i2], s[i1]
    return s

def swap_sequence(seq, nse):
    s = list(seq)
    for _ in range(nse):
        s = swap_operator(s)
    return s

def insert_operator(seq):
    s = list(seq)
    i1, i2 = random.sample(range(len(s)), 2)
    val = s.pop(i1)
    s.insert(i2, val)
    return s

def insert_sequence(seq, nse):
    s = list(seq)
    for _ in range(nse):
        s = insert_operator(s)
    return s

def run_abc(pop_size, max_iter, limit, nse, df, progress_callback=None):
    """Fungsi utama yang menjalankan algoritma ABC"""
    projek_list = df['Projek'].tolist()
    
    population = [random.sample(projek_list, len(projek_list)) for _ in range(pop_size)]
    fitnesses = [get_fitness(bee, df) for bee in population]
    trials = [0] * pop_size
    
    global_best_seq = None
    global_best_fit = -1.0
    
    for iteration in range(max_iter):
        initial_population = copy.deepcopy(population)
        initial_fitnesses = list(fitnesses)
        
        # Fase Employeed Bee (SO & SS)
        for i in range(pop_size):
            bee_so = swap_operator(population[i])
            fit_so = get_fitness(bee_so, df)
            
            if fit_so > fitnesses[i]:
                population[i], fitnesses[i], trials[i] = bee_so, fit_so, 0
            else:
                trials[i] += 1
                
            bee_ss = swap_sequence(population[i], nse)
            fit_ss = get_fitness(bee_ss, df)
            
            if fit_ss > fitnesses[i]:
                population[i], fitnesses[i], trials[i] = bee_ss, fit_ss, 0
            else:
                trials[i] += 1
                
        # Fase Selection
        total_fitness = sum(fitnesses)
        probs = [f / total_fitness for f in fitnesses] if total_fitness > 0 else [1/pop_size]*pop_size
        
        onlooker_indices = random.choices(range(pop_size), weights=probs, k=pop_size)
        onlooker_population = [list(population[idx]) for idx in onlooker_indices]
        onlooker_fitnesses = [fitnesses[idx] for idx in onlooker_indices]
        onlooker_trials = [trials[idx] for idx in onlooker_indices]

        # Fase Onlooker Bee (IO & IS)
        for i in range(pop_size):
            bee_io = insert_operator(onlooker_population[i])
            fit_io = get_fitness(bee_io, df)
            
            if fit_io > onlooker_fitnesses[i]:
                onlooker_population[i], onlooker_fitnesses[i], onlooker_trials[i] = bee_io, fit_io, 0
            else:
                onlooker_trials[i] += 1
                
            bee_is = insert_sequence(onlooker_population[i], nse)
            fit_is = get_fitness(bee_is, df)
            
            if fit_is > onlooker_fitnesses[i]:
                onlooker_population[i], onlooker_fitnesses[i], onlooker_trials[i] = bee_is, fit_is, 0
            else:
                onlooker_trials[i] += 1

        population, fitnesses, trials = onlooker_population, onlooker_fitnesses, onlooker_trials

        # Global Best update
        current_best_idx = np.argmax(fitnesses)
        if fitnesses[current_best_idx] > global_best_fit:
            global_best_fit = fitnesses[current_best_idx]
            global_best_seq = list(population[current_best_idx])

        # Fase Scout Bee
        for i in range(pop_size):
            if trials[i] > limit:
                if fitnesses[i] > initial_fitnesses[i]:
                    trials[i] = 0
                else:
                    population[i] = random.sample(projek_list, len(projek_list))
                    fitnesses[i] = get_fitness(population[i], df)
                    trials[i] = 0

        if progress_callback:
            progress_callback((iteration + 1) / max_iter)
            
    return global_best_seq, global_best_fit, calculate_makespan(global_best_seq, df)