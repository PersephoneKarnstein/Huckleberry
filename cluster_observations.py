from model import Observation, Plant, AltName, init_app 
import numpy as np 

from flask_sqlalchemy import SQLAlchemy

from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import DBSCAN
from sklearn import metrics

from alpha_shape import alpha_shape

import networkx as nx

from random import choice
from shapely.geometry import Polygon

import time
import pdb

if __name__ == "__main__": import matplotlib.pyplot as plt

init_app()
obs = Observation.query.filter_by(plant_id=548).all()
latlon = np.asarray([[a.lat, a.lon] for a in obs])
# pairwise_dists = spdist.pdist(latlon, metric='euclidean')

def order_ring(edges_set, ring_index_set):
    edge_list = np.asarray(list(edges_set))
    ring_tuplized = tuple(ring_index_set)
    starting_point = choice(ring_tuplized)
    ordered_ring = []
    while len(ring_tuplized) > len(ordered_ring):
        # print(starting_point, len(ring_tuplized), len(ordered_ring), ordered_ring)
        edge_list_index = np.where(edge_list[:,0]==starting_point)[0][0]
        ordered_ring.append(edge_list[edge_list_index][0])
        starting_point = edge_list[edge_list_index][1]
        np.delete(edge_list, edge_list_index)
    return ordered_ring

def mean_dist_to_neighbor(points):
    """Returns the mean and standard deviation of the distance from a point in [Points] to its nearest neighbor"""
    nn = NearestNeighbors(n_neighbors=2, algorithm='auto', metric='euclidean').fit(points)
    distances, indices = nn.kneighbors(latlon, return_distance=True)
    return np.mean(distances[:,1]), np.std(distances[:,1])


# #############################################################################
# Compute DBSCAN
def dbscan_mask(points, epsilon=0.3, verbose=True):
    db = DBSCAN(eps=epsilon, min_samples=10).fit(points) #previously eps=allowed_dist, but about 0.3 seems to give the best results anyway
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise_ = list(labels).count(-1)

    if verbose==True:
        print("Epsilon: %0.3f" % epsilon)
        print('Estimated number of clusters: %d' % n_clusters_)
        print('Estimated number of noise points: %d' % n_noise_)
        print("Silhouette Coefficient: %0.3f" % metrics.silhouette_score(latlon, labels))

    return {"mask":core_samples_mask, "labels":labels, "n_clusters":n_clusters_, "n_noise":n_noise_}
# #############################################################################
#  convert each cluster to a shape

# Black removed and is used for noise instead.
def get_shape(mask_info, points):
    # pdb.set_trace()
    core_samples_mask = mask_info["mask"]
    labels = mask_info["labels"]

    unique_labels = set(labels)
    colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]

    for k, col in zip(unique_labels, colors):
        if k == -1:
            # Black used for noise.
            col = [0, 0, 0, 0]

        class_member_mask = (labels == k)
        cluster_members = points[class_member_mask]
        #calculate the alpha shape only for one cluster at a time
        edges = alpha_shape(cluster_members, 0.3, only_outer=True)
        #edges contains the indices of the points, not the points themselves.

        # if __name__ == "__main__": # Plot result
        xy = points[class_member_mask & core_samples_mask]
        plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col), markeredgecolor='k', markersize=14)
        xy = points[class_member_mask & ~core_samples_mask]
        plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col), markeredgecolor='k', markersize=6)
        if k != -1:  
            for i, j in edges:
                # pdb.set_trace()
                plt.plot(cluster_members[[i, j], 0], cluster_members[[i, j], 1])



            G = nx.Graph()
            G.add_edges_from(edges)
            rings = [i for i in nx.connected_components(G)] 
            # this will give us a list of the rings of points that form each closed shape created by the alpha shape function.
            # shapely allows for shapes with holes in them, but only if the hole touches the outer edge at exactly either 0 or
            # 1 point. So we need to check to make sure that is the case. Ironically, the best way to do that is to convert all
            # the rings to shapely polygons and check whether any of them are not fully enclosed by another.

            print(f"Number of closed shapes generated within cluster {k}: {len(rings)}")

            for ring in rings:
                # in order for this to be useful, we now need to associate the indices of the points corresponding to vertices 
                # with the points themselves. Unfortunately, networkx returned the ring vertex indices as a set (and thus unordered)
                # so we first have to order the elements.
                ordered_ring_indices = order_ring(edges, ring)
                ordered_vertices = [(cluster_members[i]) for i in ordered_ring_indices]
                # pdb.set_trace()
                print(np.shape(ordered_vertices))
                # plt.plot(np.asarray(ordered_vertices).T[0], np.asarray(ordered_vertices).T[1])

                polygon = Polygon(ordered_vertices)
                plt.plot(*polygon.exterior.xy)









mask_info = dbscan_mask(latlon, verbose=True)
get_shape(mask_info, latlon)



if __name__ == "__main__":
    plt.title('Estimated number of clusters: %d' % mask_info["n_clusters"])
    plt.show()

