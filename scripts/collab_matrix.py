import pandas as pd
import numpy as np
from scipy.sparse import lil_matrix
import pickle
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def construct_collab_matrix():
    data = pd.read_csv(os.path.join(PROJECT_ROOT, 'data', 'edges.csv')).sort_values('artist_a')
    all_artist_ids = np.unique(np.concatenate((data['artist_a'].unique(), data['artist_b'].unique()), axis=None))
    collab_matrix = lil_matrix((len(all_artist_ids), len(all_artist_ids)), dtype=np.int8)
    idx_dt = {el: idx for idx, el in enumerate(all_artist_ids)}

    edgelist = data[['artist_a', 'artist_b']].astype('int32')

    def increment_weight(row):
        i = idx_dt[row['artist_a']]
        j = idx_dt[row['artist_b']]
        collab_matrix[i, j] += 1
        collab_matrix[j, i] += 1

    print("computing adjacency weights...")
    edgelist.apply(increment_weight, axis=1)
    print("done!")

    print("writing adjacency matrix to file...")

    outfile = os.path.join(PROJECT_ROOT, 'data', 'collab_matrix.pkl')
    with open(outfile, 'wb') as file:
        pickle.dump(collab_matrix, file)
    print("done!")


if __name__ == "__main__":
    construct_collab_matrix()
