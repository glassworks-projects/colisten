import pandas as pd
import numpy as np
import os
from igraph import Graph

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def get_all_artist_ids(df):
    return sorted(list(set(np.append(df['artist_a'].unique(), df['artist_b'].unique()))))


def convert_to_weighted_edgelist(df: pd.DataFrame):
    # edges must be presorted in ascending order (s.t. artist_a < artist_b)
    mx = np.sort(df[['artist_a', 'artist_b']].to_numpy(), axis=1)
    unique, counts = np.unique(mx, return_counts=True, axis=0)
    return np.c_[unique, counts]


def main():
    data = pd.read_csv(os.path.join(PROJECT_ROOT, 'data', 'edges.csv'))
    edgelist = convert_to_weighted_edgelist(data)

    g = Graph.TupleList(list(map(tuple, edgelist[:, :2].astype('str'))))

    def select_next_artist(artist: str, theta: float):
        pass


if __name__ == "__main__":
    main()
