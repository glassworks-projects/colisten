import pandas as pd
import numpy as np

data = pd.read_csv('edges.csv').sort_values('artist_a')
all_artist_ids = np.unique(np.concatenate((data['artist_a'].unique(), data['artist_b'].unique()), axis=None))
collab_matrix = np.zeros((len(all_artist_ids), len(all_artist_ids)))
idx_dt = {el: idx for idx, el in enumerate(all_artist_ids)}

edgelist = data[['artist_a', 'artist_b']].astype('int32')


def increment_weight(row):
    i = idx_dt[row['artist_a']]
    j = idx_dt[row['artist_b']]
    collab_matrix[i,j] += 1
    collab_matrix[j,i] += 1


edgelist.apply(increment_weight, axis=1)
