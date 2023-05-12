import pandas as pd
import numpy as np
from igraph import Graph
from scipy.stats import rankdata


class ArtistNetwork:
    def __init__(self, data_path: str, prevent_loops=True, use_ranking=False):
        # TODO: guard against malformed data path
        self.data = pd.read_csv(data_path)
        print("converting data to weighted edgelist...")
        self.edgelist = self.__convert_to_weighted_edgelist(self.data)
        print("done!")
        print("constructing graph...")
        self.graph = Graph.TupleList(
            list(map(lambda x: (x[0].astype(str), x[1].astype(str), self.__scale(x[2])), self.edgelist)),
            weights=True
        )
        print("done!")
        self.prevent_loops = prevent_loops
        self.use_ranking = use_ranking
        self.last_artist_id = None

    @staticmethod
    def __convert_to_weighted_edgelist(df: pd.DataFrame):
        # edges must be presorted in ascending order (s.t. artist_a < artist_b)
        mx = np.sort(df[['artist_a', 'artist_b']].to_numpy(), axis=1)
        unique, counts = np.unique(mx, return_counts=True, axis=0)
        return np.c_[unique, counts]

    @staticmethod
    def __scale(weight: int):
        # TODO: experiment with this
        return 1 / weight

    # TODO experiment with suitable settings of theta
    def select_next_artist(self, artist_id: str, theta: float, subgraph_order: int = 2):
        if subgraph_order > 2:
            print("max subgraph order is 2 (for now). {} is too large.".format(subgraph_order))
            subgraph_order = 2

        if theta > 5:  # TODO experiment with this
            print("max setting for theta is 5 (for now). {} is too large.".format(theta))
            theta = 5

        lengths_dict = self.__path_lengths(artist_id, order=subgraph_order)
        lengths = np.array(list(lengths_dict.values()))
        probs = self.__probability(lengths, theta)
        res = str(np.random.choice(list(lengths_dict.keys()), p=probs))
        self.last_artist_id = res
        return res

    # modified softmax
    # TODO guard against overflow
    # TODO normalize?
    @staticmethod
    def __probability(lengths: np.ndarray, theta: float):
        x = np.exp(theta * 1 / lengths)
        return x / sum(x)

    def __path_lengths(self, artist_id: str, order: int = 1):
        # for each vertex in subgraph, find path length from that vertex to focal_vertex
        # return: {vertex : length}
        # TODO: can we do this without getting vertex_id, i.e., using "name"?
        focal_vertex_id = self.graph.vs()['name'].index(artist_id)
        subgraph = self.__ego_subgraph(self.graph, focal_vertex_id, order)
        # find new vertex ID in subgraph
        focal_vertex_id = subgraph.vs()['name'].index(artist_id)
        shortest_paths = subgraph.get_shortest_paths(focal_vertex_id, weights='weight')

        artist_ids = []
        lengths = []
        for path in shortest_paths:
            artist_ids.append(subgraph.vs()[path[-1]]['name'])
            lengths.append(self.__compute_single_path_length(subgraph, path))

        if self.use_ranking:
            lengths = rankdata(lengths)

        res = dict(zip(artist_ids, lengths))

        # artificially inflate path length (or rank) to last visited vertex to discourage looping
        if self.last_artist_id and self.last_artist_id in res.keys() and self.prevent_loops:
            if self.use_ranking:
                # note: this messes up ranking, watch for side effects
                res[self.last_artist_id] = len(res.values())
            else:
                res[self.last_artist_id] = max(res.values()) + 1

        res.pop(artist_id)
        return res

    @staticmethod
    def __ego_subgraph(g: Graph, vertex_id: int, order: int = 1):
        return g.induced_subgraph(g.neighborhood(vertex_id, order))

    @staticmethod
    def __compute_single_path_length(g: Graph, path):
        path_iter = iter(path)

        def path_recursive(a, length):
            try:
                b = next(path_iter)
                length += g[a, b]
                return path_recursive(b, length)
            except StopIteration:
                return length

        return path_recursive(next(path_iter), 0)

    def set_loop_prevention(self, prevent_loops: bool) -> None:
        self.prevent_loops = prevent_loops

    def set_use_ranking(self, use_ranking: bool) -> None:
        self.use_ranking = use_ranking
