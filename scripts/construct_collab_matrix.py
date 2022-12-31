import pandas as pd
import numpy as np
from scipy.sparse import lil_matrix
import pickle
import os


def construct_collab_matrix(index_dict: dict, edgelist: pd.DataFrame, write_dir: str):
    collab_matrix = lil_matrix((len(index_dict), len(index_dict)), dtype=np.int8)

    def increment_weight(row):
        i = index_dict[row['artist_a']]
        j = index_dict[row['artist_b']]
        collab_matrix[i, j] += 1
        collab_matrix[j, i] += 1

    print("computing adjacency weights...")
    edgelist.apply(increment_weight, axis=1)
    print("done!")

    print("writing adjacency matrix to file...")

    outfile = os.path.join(write_dir, 'collab_matrix.pkl')
    with open(outfile, 'wb') as file:
        pickle.dump(collab_matrix, file)
    print("done!")
