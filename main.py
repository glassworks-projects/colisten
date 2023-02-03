import pandas as pd
import numpy as np
import os
from igraph import Graph

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


# def get_all_artist_ids(df):
#     return sorted(list(set(np.append(df['artist_a'].unique(), df['artist_b'].unique()))))


def convert_to_weighted_edgelist(df: pd.DataFrame):
    # edges must be presorted in ascending order (s.t. artist_a < artist_b)
    mx = np.sort(df[['artist_a', 'artist_b']].to_numpy(), axis=1)
    unique, counts = np.unique(mx, return_counts=True, axis=0)
    return np.c_[unique, counts]


# TODO: decide if we really need to do this, given that computing for the entire graph is reasonably fast
def ego_subgraph(g: Graph, vertices, order=1):
    return g.induced_subgraph(g.neighborhood(vertices, order))


def path_lengths(g: Graph, focal_vertex: str, order=1):
    # for each vertex in subgraph, find path length from that vertex to focal_vertex
    # return: {vertex : length}
    subgraph = ego_subgraph(g, focal_vertex, order)
    shortest_paths = subgraph.get_shortest_paths(focal_vertex, weights='weight')
    return {subgraph.vs()[path[-1]]['name']: compute_single_path_length(subgraph, path) for path in shortest_paths}


def compute_single_path_length(graph, path):
    def path_recursive(idx, length):
        if idx == len(path) - 1:
            return length
        length += graph[path[idx], path[idx+1]]
        return path_recursive(idx+1, length)
    return path_recursive(0, 0)


def scale(weight: int):
    # TODO: experiment with this
    return 1/weight


def main():
    data = pd.read_csv(os.path.join(PROJECT_ROOT, 'data', 'edges.csv'))
    print("converting to weighted edgelist...")
    edgelist = convert_to_weighted_edgelist(data)
    print("done!")

    # TODO faster?? can we not convert this on the fly?
    # TODO convert weights here or later?
    print("constructing graph...")
    g = Graph.TupleList(
        list(map(lambda x: (x[0].astype(str), x[1].astype(str), scale(x[2])), edgelist)),
        weights=True
    )
    print("done!")

    print(path_lengths(g, '1', order=2))

    def select_next_artist(artist: str, theta: float):
        pass


if __name__ == "__main__":
    main()
