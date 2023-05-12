import os
from artist_network import ArtistNetwork

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def main():
    data_path = os.path.join(PROJECT_ROOT, 'data', 'edges.csv')
    network = ArtistNetwork(data_path, use_ranking=True)

    # TODO faster?? can we not convert this on the fly?
    # TODO convert weights here or later?

    artist = "417"

    for i in range(10):
        next_artist = network.select_next_artist(artist, 0.9)
        print(next_artist)
        artist = next_artist


if __name__ == "__main__":
    main()
