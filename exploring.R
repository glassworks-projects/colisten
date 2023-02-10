#load libraries
library(igraph)
library(tnet)

#set workspace and load data (note that edges are already presorted in ascending order)
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

#add vertex names that can persist to subgraph
V(graph)$name <- as.character(V(graph))

subnet <- make_ego_graph(graph, nodes = 300, order = 2)

#plot subnetwork of order 2 around node 300, with edgelists
plot(make_ego_graph(graph, nodes = 300, order = 2)[[1]], vertex.label = "", vertex.color = "grey", vertex.size = 5, edge.width = E(graph)$weight)

#function for summing path lengths from focal node to all other nodes in subnetwork, taking inverse weight into account
#note that paths includes the focal node and assigns path length of 0, so we're dropping that
path_constructor <- function(object, focal){
  paths <- as.numeric(shortest.paths(object, v = which(V(object)$name == focal), weights = E(object)$inv_weight))
  return(paths[which(paths > 0)])
}

#function for getting the probability of jumping from the focal node to each other node in the network, using a modified softmax transformation
softmax <- function(object, focal, dist_param){
  paths <- path_constructor(object, focal)
  denom <- sum(exp(dist_param*(1/paths)))
  return(sapply(1:length(paths), function(x){exp(dist_param*(1/paths[x]))/denom}))
}

#plot the resulting probability weights for parameter values between 0 and 0.5
par(mar = c(4.5, 4.5, 0.8, 0.8))
matplot(sapply(seq(0, 0.5, by = 0.05), function(x){sort(softmax(subnet[[1]], 300, x), decreasing = TRUE)}), type = "l", lty = 1, xlab = "Nodes", ylab = ("Probability Weight"), log = "x")

#function for taking a full graph object with weights, getting subnetwork, calculating paths and converting to probabilities, and getting a new focal node
algorithm <- function(object, focal, order, dist_param){
  subnet <- make_ego_graph(object, nodes = focal, order = order)
  probs <- softmax(subnet[[1]], focal, dist_param)
  return(sample(V(subnet[[1]])$name[-which(V(subnet[[1]])$name == focal)], 1, prob = probs))
}


