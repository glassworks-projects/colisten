import pandas as pd
import os
import networkx as nx

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def main():
    data = pd.read_csv(os.path.join(PROJECT_ROOT, 'data', 'edges.csv')).sort_values('artist_a')

    edgelist = dict()

    def evaluate_row(row):
        k = frozenset([row['artist_a'], row['artist_b']])
        if k in edgelist:
            edgelist[k] += 1
        else:
            edgelist[k] = 1

    data.apply(evaluate_row, axis=1)
    g = nx.Graph()

    for key, value in edgelist.items():
        a, b = [vtx for vtx in iter(key)]
        g.add_edge(a, b, weight=value)

    def select_next_artist(artist: str, theta: float):
        pass


if __name__ == "__main__":
    main()
