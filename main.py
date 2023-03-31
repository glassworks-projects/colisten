import pandas as pd
import numpy as np
import os
from igraph import Graph

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PREVENT_LOOPS = True
last_artist_id = ""


def convert_to_weighted_edgelist(df: pd.DataFrame):
    # edges must be presorted in ascending order (s.t. artist_a < artist_b)
    mx = np.sort(df[['artist_a', 'artist_b']].to_numpy(), axis=1)
    unique, counts = np.unique(mx, return_counts=True, axis=0)
    return np.c_[unique, counts]


def ego_subgraph(g: Graph, vertex_id: int, order: int = 1):
    return g.induced_subgraph(g.neighborhood(vertex_id, order))


def path_lengths(g: Graph, artist_id: str, order=1):
    # for each vertex in subgraph, find path length from that vertex to focal_vertex
    # return: {vertex : length}
    # TODO: can we do this without getting vertex_id, i.e., using "name"?
    focal_vertex_id = g.vs()['name'].index(artist_id)
    subgraph = ego_subgraph(g, focal_vertex_id, order)
    # find new vertex ID in subgraph
    focal_vertex_id = subgraph.vs()['name'].index(artist_id)
    shortest_paths = subgraph.get_shortest_paths(focal_vertex_id, weights='weight')

    res = {subgraph.vs()[path[-1]]['name']: compute_single_path_length(subgraph, path) for path in shortest_paths}

    # artificially inflate path length to last visited vertex to discourage looping
    if last_artist_id and PREVENT_LOOPS:
        res[last_artist_id] = max(res.values()) + 1

    res.pop(artist_id)
    return res


# modified softmax
# TODO guard against overflow
# TODO normalize?
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


# TODO experiment with suitable settings of theta
def select_next_artist(g: Graph, artist_id: str, theta: float, subgraph_order: int = 2):
    global last_artist_id
    if subgraph_order > 2:
        print("max subgraph order is 2 (for now). {} is too large.".format(subgraph_order))
        subgraph_order = 2

    if theta > 5:  # TODO experiment with this
        print("max setting for theta is 5 (for now). {} is too large.".format(theta))
        theta = 5

    lengths_dict = path_lengths(g, artist_id, order=subgraph_order)
    lengths = np.array(list(lengths_dict.values()))
    probs = probability(lengths, theta)
    return str(np.random.choice(list(lengths_dict.keys()), p=probs))


def main():
    global last_artist_id
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

    artist = "417"

    for i in range(10):
        next_artist = select_next_artist(g, artist, 0.9)
        print(next_artist)

        # TODO: this juggling of artist IDs needs formalizing
        last_artist_id = artist
        artist = next_artist


if __name__ == "__main__":
    main()
