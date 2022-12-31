import pandas as pd
import os
import networkx as nx

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def main():
    data = pd.read_csv(os.path.join(PROJECT_ROOT, 'data', 'edges.csv'))
    g = nx.Graph()

    def construct_graph(row):
        a = row['artist_a']
        b = row['artist_b']
        if (a, b) in g.edges:
            g.edges[(a, b)]['weight'] += 1
        else:
            g.add_edge(a, b, weight=1)

    print('constructing graph...')
    data.apply(construct_graph, axis=1)
    print('done!')

    def select_next_artist(artist: str, theta: float):
        pass


if __name__ == "__main__":
    main()
