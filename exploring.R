#load libraries
library(igraph)
library(tnet)

#set workspace and load data
setwd("~/Documents/Work/Fall 2022/Music Algorithm")
edges <- read.csv("edges.csv")

#convert arbitrary character nodes to arbitrary numeric nodes (makes igraph friendlier)
all_nodes <- sort(unique(c(edges$artist_a, edges$artist_b)))
edges$artist_a <- as.numeric(factor(edges$artist_a, levels = all_nodes))
edges$artist_b <- as.numeric(factor(edges$artist_b, levels = all_nodes))

#compress unweighted network to weighted network
w_edges <- shrink_to_weighted_network(edges[, c(3:4)])

#convert edgelist to igraph object
graph <- graph_from_edgelist(as.matrix(w_edges[, 1:2]), directed = FALSE)

#add weights (+ inverse) to igraph object from third column of weighted edgelist
E(graph)$weight <- w_edges[, 3]
E(graph)$inv_weight <- 1/E(graph)$weight

#get ego subnetwork of order 2 around node 300
subnet <- make_ego_graph(graph, nodes = 300, order = 2)[[1]]

#plot subnetwork of order 2 around node 300, with edgelists
plot(subnet, vertex.label = "", vertex.color = "grey", vertex.size = 5, edge.width = E(graph)$weight)
