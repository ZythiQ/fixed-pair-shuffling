import pickle, numpy as np, pandas as pd, matplotlib.pyplot as plt, seaborn as sns # type: ignore

from collections import Counter


def load_data(filepath:str) -> object:
    '''Unpickles a saved object.'''
    
    with open(filepath, 'rb') as file:
        return pickle.load(file)


def get_pair_occurrence(filepath: str):
    '''Finds distinct pairs and co-occurrences.'''

    coccurence = Counter()
    all_pairs = Counter()
    
    for _, combo in load_data(filepath): # type: ignore
        distinct = list(set(combo))
        all_pairs.update(combo)
        
        for i, pair1 in enumerate(distinct):
            for j, pair2 in enumerate(distinct):
                if i < j:
                    coccurence[(pair1, pair2)] += 1
    
    distinct = sorted(list(all_pairs.keys()))
    num_dist = len(distinct)
    
    matrix = np.empty((num_dist + 1, num_dist + 1), dtype=object)
    matrix[0, 0] = ""

    for i, pair in enumerate(distinct):
        matrix[0, i + 1] = pair # First row
        matrix[i + 1, 0] = pair # First column
    
    pix = {pair: i for i, pair in enumerate(distinct)}

    for i, pair1 in enumerate(distinct):
        for j, pair2 in enumerate(distinct):
            if i == j:
                matrix[i + 1, j + 1] = 0 
            else:
                key1 = (pair1, pair2) if pix[pair1] < pix[pair2] else (pair2, pair1)
                matrix[i + 1, j + 1] = coccurence.get(key1, 0)
    
    return all_pairs, matrix


def make_matrix_heatmap(matrix, filepath:str):
    '''Saves a heat map of a labeled co-occurrence matrix.'''

    labels = matrix[0, 1:].tolist()
    data = matrix[1:, 1:].astype(float)
    
    df = pd.DataFrame(data, index=labels, columns=labels)
    plt.figure(figsize=(12, 10))
    
    sns.heatmap(df, annot=True, cmap='Blues', fmt='g', xticklabels=True, yticklabels=True)
    
    plt.gca().xaxis.tick_top()
    plt.gca().xaxis.set_label_position('top')
    
    plt.xticks(rotation=45, ha='left')
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    plt.savefig(filepath)


def as_binary(matrix):
    '''Converts a labeled co-occurrence matrix into a flat list of binary values.'''
    return ((matrix[1:, 1:] != 0).astype(int)).flatten().tolist()


if __name__ == '__main__':
    matrices = []
    pickles = [
        'pruned_S2_P1_C1_D0.pkl',
        'pruned_S3_P3_C6_D2.pkl',
        'pruned_S4_P5_C96_D8.pkl',
        'pruned_S5_P8_C1920_D56.pkl'
    ]

    for pkl in pickles:
        distict, matrix = get_pair_occurrence(f'data/pickled/{pkl}')
        matrices.append(matrix)

        print(f'{pkl} -> {distict}')
        print(f'{pkl} -> {as_binary(matrix)}')

    [make_matrix_heatmap(m, f'data/figures/{p.rstrip(".pkl")}') for m, p in zip(matrices, pickles)]
