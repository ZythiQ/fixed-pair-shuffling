from itertools import islice, chain, combinations, permutations
from concurrent.futures import ProcessPoolExecutor
from math import factorial, comb, perm
from multiprocessing import cpu_count
from collections import Counter
from typing import Iterator
from tqdm import tqdm


class PearTree:
    '''
    Sequence/combination memoization tree.
    '''

    class Pear:
        '''
        A PearTree node.
        '''

        def __init__(self, sequences:Counter[tuple[int, ...]], n:int, m:int) -> None:
            '''
            Initializes the Pear.
            '''
            self.leaves = {}
            self.sequences = sequences
            self.bad = len(self.sequences) < PearTree.A089827(n, m)            


        def find_sequence_permutations(self, combination:tuple[tuple[int, int], ...], n:int) -> Counter | None:
            '''
            Lazily swaps index-pairs in order (50% probability) and returns a permutation frequency map.
            '''
            pear = self

            for m, pair in enumerate(combination):
                if pear is None or pear.bad:
                    break
                
                if pair not in pear.leaves:
                    counter = pear.sequences.copy()
                    i, j = pair

                    for seq, count in pear.sequences.items():
                        new_seq = list(seq[:])
                        new_seq[i], new_seq[j] = seq[j], seq[i]
                        counter.update({seq: count, tuple(new_seq): count})

                    pear.leaves.update({pair: PearTree.Pear(counter, n, m)})

                pear = pear.leaves.get(pair)
                
            return pear.sequences if pear else None
    

        def batch_find_sequence_permutations(self, combinations:Iterator[tuple[tuple[int, int], ...]], n:int) -> list:
            '''
            Batch find sequence permutations and prepend with the associated index-pair combination.
            '''
            return [(combo, self.find_sequence_permutations(combo, n)) for combo in combinations]
    

    @staticmethod
    def A006218(n:int) -> int:
        '''
        Returns the minimal number of lazy swaps for an n-element sequence.
        '''
        return sum((n - 1) // k for k in range(1, n))


    @staticmethod
    def A089827(n:int, m:int) -> int:
        '''
        Returns the lower bound of the m-th pair (1 ≤ m ≤ 23) in the optimal pairing of an n-element sequence.
        '''
        return (n < 5) or (1, 2, 4, 8, 16, 24, 48, 80, 160, 320, 640, 1280, 2560, 3840, 7680, 15360, 30720, 61440, 122880, 184320, 368640, 737280, 1474560, 2949120)[m]
    

    @staticmethod
    def half_permutations(n:int, m:int, chunk_size:int) -> Iterator:
        '''
        Returns reversible m-pair permutations of an n-element sequence as iterable chunks. 
        '''
        perms = (p for p in permutations(combinations(range(n), 2), m) if p <= p[::-1])

        # return (chain([first], islice(perms, chunk_size - 1)) for first in perms) # Damn pickles
        while chunk := islice(perms, chunk_size): # Touching each combo is too slow...
            yield list(chunk)


    @staticmethod
    def find_pair_combinations(n:int, chunk_size:int = 100000) -> list:
        '''
        Returns a list of index-pair combinations that fully shuffle an n-element sequence.
        '''
        opt_combs = []

        max_pairs = comb(n, 2)
        min_pairs = PearTree.A006218(n)
        expected_sequences = factorial(n)

        sequence = Counter({tuple(range(n)): 1})
        pears = [PearTree.Pear(sequence.copy(), n, 0) for _ in range(max(cpu_count(), 4))]
        
        while min_pairs <= max_pairs:
            
            total = perm(max_pairs, min_pairs) // 2
            combs = PearTree.half_permutations(n, min_pairs, chunk_size)

            with tqdm(combs, total=total, desc=f'Searching {min_pairs}-pair combs') as bar, ProcessPoolExecutor() as exe:
                if n <= 2:
                    bar.update(total)
                    return list(combinations(range(2), 2))
                
                while bar.n < total:
                    futures = [exe.submit(p.batch_find_sequence_permutations, c, n) for p, c in zip(pears, combs)]

                    for future in futures:
                        for combo, counter in future.result():
                            if counter and len(counter) == expected_sequences:
                                opt_combs.extend([combo, tuple(reversed(combo))])
                            bar.update()

            if opt_combs: break
            min_pairs += 1
                
        return opt_combs


def main(i:int, j:int = 0):
    '''
    Finds index-pair combinations for sequences length (2 ≤ i ≤ j).
    '''
    if i > 1:
        for size in (range(i, j + 1) if i < j else [i]):
            print(len(PearTree.find_pair_combinations(size)))


if __name__ == '__main__':
    main(5)
