import os, csv, math, heapq, pickle, itertools as it

from collections import Counter
from tqdm import tqdm


class PearTree:
    '''
    Sequence/combination memoization tree.
    '''

    class Pear:
        '''
        A PearTree node.
        '''

        def __init__(self, counter:Counter, bad:bool = False) -> None:
            '''
            Initializes the Pear.
            '''
            self.bad = bad
            self.leaves = dict()
            self.counter = counter
    

    def __init__(self, batch:int = 1000) -> None:
        '''
        Initializes the PearTree.
        '''
        self.batch = batch
        self.root = PearTree.Pear(Counter())


    def __A089827(self, n:int) -> int:
        '''
        Returns the lower-number of sequences for the {1..20} n-th pair in an optimal combination.
        '''
        return [2, 4, 8, 16, 24, 48, 80, 160, 320, 640, 1280, 2560, 3840, 7680, 15360, 30720, 61440, 122880, 184320, 368640][n - 1]
    

    def __A006218(self, n:int) -> int:
        '''
        Returns the lower-number of pairs to lazily swap a n-element sequence.
        '''
        return sum((n - 1) // k for k in range(1, n))


    def find_permutations(self, combination:tuple[tuple[int, int], ...]) -> Counter|None:
        '''
        Lazily applies the pairs in combination and returns the frequency map of the root sequence's permutations.
        '''
        pear = self.root

        for ix, pair in enumerate(combination):
            if pear is None or pear.bad:
                break
            
            if pair not in pear.leaves:
                counter = pear.counter.copy()
                i, j = pair

                for seq, count in pear.counter.items():
                    new_seq = list(seq[:])
                    new_seq[i], new_seq[j] = seq[j], seq[i]
                    counter.update({seq: count, tuple(new_seq): count})

                pear.leaves.update({
                    pair: PearTree.Pear(counter, len(counter) < self.__A089827(ix + 1))
                })

            pear = pear.leaves.get(pair)
            
        return pear.counter if pear else None

    
    def find_combinations(self, sequence:tuple[int, ...]) -> list:
        '''
        Finds all pair combinations that fully shuffle the sequence.
        '''
        optimal = []

        n = len(sequence)
        m = math.factorial(n)
        min_dupe = float('inf')
        
        max_pairs = math.comb(n, 2)
        min_pairs = self.__A006218(n)
        
        all_pairs = list(it.combinations(range(n), 2))
        self.root = PearTree.Pear(Counter({sequence:1}))

        while min_pairs <= max_pairs:
            total = math.perm(max_pairs, min_pairs)
            combos = it.permutations(all_pairs, min_pairs)

            with tqdm(combos, total=total, desc=f'Computing {min_pairs}-pair combos') as progress:
                for combo in combos:
                    counter = self.find_permutations(combo)

                    if counter and len(counter) == m:
                        dupes = sum(c for c in counter.values() if c > 1)
                        
                        if dupes < min_dupe:
                            optimal = [combo]
                            min_dupe = dupes
                            
                        elif dupes == min_dupe:
                            optimal.append(combo)

                    progress.update()

                if optimal:
                    progress.colour = 'green'
                    break

            progress.colour = 'red'
            min_pairs += 1
        
        return optimal
    

def save_combos(combinations:list[tuple[tuple[int, int], ...]], filename:str, save_dir:str):
    '''Saves the a list of combinations as a Pickle and CSV.'''

    os.makedirs(save_dir, exist_ok=True)
    os.makedirs(f'{save_dir}/csv', exist_ok=True)
    os.makedirs(f'{save_dir}/pickled', exist_ok=True)

    with open(f"{save_dir}/pickled/{filename}.pkl", 'wb') as file:
        pickle.dump(combinations, file)
    
    with open(f"{save_dir}/csv/{filename}.csv", 'w', newline='') as file:
        writer = csv.writer(file)

        for combo in sorted(combinations):
            writer.writerow([f'({i}, {j})' for i, j in combo])


if (__name__ == '__main__'):
    '''
    Naive brute-forcing optimal pair swaps.
    '''
    tree = PearTree()

    for i in range(2, 5 + 1):
        combos = tree.find_combinations(tuple(n for n in range(1, i + 1)))

        save_combos(combos, f'S{i}_P{len(combos[0]) if combos else 0}_C{len(combos)}', 'data')
