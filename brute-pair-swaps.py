import math, heapq, csv, pickle, itertools as it, multiprocessing as mp

from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm


def get_combos(sequence:list, pairs:tuple) -> tuple[int, int, tuple]:
    '''Returns the pairs used, number of distinct sequences, and duplicates.'''
    
    fmap = dict()
    
    def get_seqs(cur_seq:list, depth:int):
        '''Recursively generates sequences w/a pair/depth.'''

        if depth >= len(pairs):
            seq_tup = tuple(cur_seq)
            fmap[seq_tup] = fmap.get(seq_tup, 0) + 1
            return
        
        i, j = pairs[depth]

        new_seq = cur_seq[:]
        new_seq[i], new_seq[j] = new_seq[j], new_seq[i]

        get_seqs(cur_seq[:], depth + 1)
        get_seqs(new_seq, depth + 1)
    
    get_seqs(sequence[:], 0)
    return sum(1 for v in fmap.values() if v > 1), len(fmap), pairs


def batch_get_combos(sequence:list, pair_groups:list[tuple]):
    '''Batch processes pair combos with get_combos().'''
    return [get_combos(sequence, group) for group in pair_groups]


def get_optimal_pairs(sequence:list, chunk_size:int = 1000, prune_duplicates:bool = True) -> list[tuple[int, tuple]]:
    '''Returns the optimal sequential pairs to shuffle the given integer sequence.'''
    
    optimal = []
    min_dup = float('inf')
    
    n = len(sequence)
    m = math.factorial(n)
    p = list(it.combinations(range(n), 2))
    
    max_pairs = math.comb(n, 2)
    min_pairs = sum((n - 1) // k for k in range(1, n))
    
    while min_pairs <= max_pairs:
        total = math.factorial(max_pairs) // (2 if n > 2 else 1)
        combos = it.islice(it.permutations(p, min_pairs), total)
        
        with ProcessPoolExecutor() as executor, tqdm(combos, total=total, desc=f'Computing {min_pairs}-pair combos') as progress:
            while (chonk := list(it.islice(combos, chunk_size))):

                workers = min(mp.cpu_count() or 4, len(chonk))
                chunks = [c for i in range(workers) if (c := chonk[i::workers])]
                futures = [executor.submit(batch_get_combos, sequence, chunk) for chunk in chunks]

                for future in futures:
                    chunk_result = future.result()

                    for result in chunk_result:
                        dups, distict, combo = result
                    
                        if distict == m:
                            bizarro = tuple(reversed(combo))

                            if prune_duplicates:
                                if dups < min_dup:
                                    optimal = [(dups, combo), (dups, bizarro)] if n > 2 else [(dups, combo)]
                                    min_dup = dups
                                    
                                elif dups == min_dup:
                                    heapq.heappush(optimal, (dups, combo))
                                    heapq.heappush(optimal, (dups, bizarro))
                            else:
                                optimal.extend([(dups, combo), (dups, bizarro)])

                    progress.update(len(chunk_result))

            if optimal:
                progress.colour = 'green'
                break

            progress.colour = 'red'
            min_pairs += 1

    return optimal


def save_optimal_pairs(sequence:list, prune_duplicates:bool = True, data_dir:str = 'data'):
    '''Generates and saves the optimal pairs as CSV and PKL.'''

    results = sorted(get_optimal_pairs(sequence, prune_duplicates=prune_duplicates))
    pairs = len(results[0][1])
    count = len(results)
    dups = results[0][0]

    filename = f'{"" if prune_duplicates else "un"}pruned_S{len(sequence)}_P{pairs}_C{count}_D{dups}'
    
    with open(f'{data_dir}/csv/{filename}.csv', 'w', newline='') as file:
        writer = csv.writer(file)

        for dups, pairs in results:
            writer.writerow([f'({a}, {b})' for a, b in pairs])

    with open(f'{data_dir}/pickled/{filename}.pkl', 'wb') as file:
        pickle.dump(results, file)


if __name__ == '__main__':
    for n in range(6, 6 + 1):
        save_optimal_pairs([m for m in range(n)])
