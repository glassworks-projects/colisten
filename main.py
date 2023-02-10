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
def ego_subgraph(g: Graph, vertex_id: int, order: int = 1):
    return g.induced_subgraph(g.neighborhood(vertex_id, order))


def path_lengths(g: Graph, focal_vertex_id: int, order=1):
    # for each vertex in subgraph, find path length from that vertex to focal_vertex
    # return: {vertex : length}
    subgraph = ego_subgraph(g, focal_vertex_id, order)
    shortest_paths = subgraph.get_shortest_paths(focal_vertex_id, weights='weight')
    res = {subgraph.vs()[path[-1]]['name']: compute_single_path_length(subgraph, path) for path in shortest_paths}
    res.pop(subgraph.vs()[focal_vertex_id]['name'])
    return res


# modified softmax
def probability(lengths: np.ndarray, theta: float):
    x = np.exp(theta / lengths)
    return x / sum(x)


def compute_single_path_length(graph, path):
    path_iter = iter(path)

    def path_recursive(a, length):
        try:
            b = next(path_iter)
            length += graph[a, b]
            return path_recursive(b, length)
        except StopIteration:
            return length

    return path_recursive(next(path_iter), 0)


def scale(weight: int):
    # TODO: experiment with this
    return 1 / weight


def select_next_artist(g: Graph, artist: str, theta: float, subgraph_order: int = 2):
    artist_vertex_id = g.vs['name'].index(artist)
    lengths_dict = path_lengths(g, artist_vertex_id, order=subgraph_order)
    lengths = np.array(list(lengths_dict.values()))
    probs = probability(lengths, theta)
    return np.random.choice(list(lengths_dict.keys()), p=probs)


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

    print("sampling for artist 300 ten times: ...")
    for i in range(10):
        print(select_next_artist("300", 50))


if __name__ == "__main__":
    main()
