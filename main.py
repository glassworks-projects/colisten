import pandas as pd
import numpy as np
import pickle
import os
from scripts.construct_collab_matrix import construct_collab_matrix

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def main():
    data = pd.read_csv(os.path.join(PROJECT_ROOT, 'data', 'edges.csv')).sort_values('artist_a')
    all_artist_ids = np.unique(np.concatenate((data['artist_a'].unique(), data['artist_b'].unique()), axis=None))
    idx_dt = {el: idx for idx, el in enumerate(all_artist_ids)}
    edgelist = data[['artist_a', 'artist_b']].astype('int32')

    data_dir = os.path.join(PROJECT_ROOT, 'data')
    matrix_file = os.path.join(data_dir, 'collab_matrix.pkl')

    if os.path.exists(matrix_file):
        print('adjacency matrix exists. loading from disk...')
        with open(matrix_file, 'rb') as file:
            collab_matrix = pickle.load(file)
            print('done!')
    else:
        print('adjacency matrix not found in data directory. constructing...')
        collab_matrix = construct_collab_matrix(idx_dt, edgelist, data_dir)


if __name__ == "__main__":
    main()
