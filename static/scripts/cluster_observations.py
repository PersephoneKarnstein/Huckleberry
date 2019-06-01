from server import app
from model import Observation, DistPoly, connect_to_db, db 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

import numpy as np 
import matplotlib.pyplot as plt
import networkx as nx
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import cascaded_union, polygonize
from scipy.spatial.qhull import QhullError

from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import DBSCAN
from sklearn import metrics
from random import choice
from tqdm import tqdm, tqdm_gui
import time, pdb, geoalchemy2

from alpha_shape import alpha_shape
from inaturalist_handler import get_inat_obs


connect_to_db(app)
db.create_all()

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
    distances, indices = nn.kneighbors(points, return_distance=True)
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
        print("DBSCAN Epsilon: %0.3f" % epsilon)
        print('Estimated number of clusters: %d' % n_clusters_)
        print('Estimated number of noise points: %d' % n_noise_)
        print("Silhouette Coefficient: %0.3f" % metrics.silhouette_score(points, labels))

    return {"mask":core_samples_mask, "labels":labels, "n_clusters":n_clusters_, "n_noise":n_noise_}
# #############################################################################
#  convert each cluster to a shape

# Black removed and is used for noise instead.
def get_shape(mask_info, points, plant_id, plot=False):
    core_samples_mask = mask_info["mask"]
    labels = mask_info["labels"]

    unique_labels = set(labels)
    colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]

    # polygon_conversion.set_description('\x1b[1;37;45mConverting ' +(plant_name if len(plant_name)<23 else plant_name[:20]+"...")+ '\x1b[0m')
    
    for k, col in zip(unique_labels, colors): #everything within this for loop is operating on a single cluster.
        if plot:
            if k == -1:
                # Black used for noise.
                col = [0, 0, 0, 0]

        class_member_mask = (labels == k)
        cluster_members = points[class_member_mask]
        if len(cluster_members) < 4:
            continue
        else:
            #calculate the alpha shape only for one cluster at a time
            if k != -1: 
                epsilon = 0.1
                cluster_polygon = cluster_to_polygon(cluster_members, epsilon, k, verbose=False)
                cluster_stats = mean_dist_to_neighbor(points)

                if not cluster_polygon.is_valid:
                    cluster_polygon = clean_polygon(cluster_polygon, cluster_stats[1]/2.)
                else: pass

                # print(type(cluster_polygon))

            if plot: # Plot result
                xy = points[class_member_mask & core_samples_mask]
                plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col), markeredgecolor='k', markersize=14)
                xy = points[class_member_mask & ~core_samples_mask]
                plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col), markeredgecolor='k', markersize=6)

                if k != -1:  
                    # plt.plot(*cluster_polygon.exterior.xy)
                    # try: plt.plot(*cluster_polygon.interior.xy)
                    # except AttributeError: pass
                    try:
                        plt.plot(*cluster_polygon.buffer(cluster_stats[0]+2*cluster_stats[1]).exterior.xy)
                    except AttributeError:
                        raise AttributeError("\n\n!!!!Multipolygon Detected!!!\n\n")

                    try: plt.plot(*cluster_polygon.buffer(cluster_stats[0]+2*cluster_stats[1]).interior.xy)
                    except AttributeError: pass


            if k != -1:
                add_poly_to_table(cluster_polygon.buffer(cluster_stats[0]+2*cluster_stats[1]), plant_id)

    db.session.commit()

def clean_polygon(polygon, buffer):
    """turns a self-intersecting polygon into a valid (non-self-intersecting) one"""
    pe = polygon.exterior
    mls = pe.intersection(pe)
    polygons = list(polygonize(mls))
    return cascaded_union([a.buffer(buffer) for a in polygons])


def cluster_to_polygon(points_in_cluster, epsilon_0, k, verbose=True):#, plot=False):
    if verbose: print("Alpha shape: testing with epsilon = %0.3f" % epsilon_0)
    while True:
        try:
            edges = alpha_shape(points_in_cluster, epsilon_0, only_outer=True)
            break
        except QhullError:
            if epsilon_0>2:
                edges = []
            else:
                epsilon_0 += 0.01
                print(f"Updated epsilon_0 to {epsilon_0}.")

    #edges contains the indices of the points, not the points themselves.

    G = nx.Graph()
    G.add_edges_from(edges)
    rings = [i for i in nx.connected_components(G)] 
    # this will give us a list of the rings of points that form each closed shape created by the alpha shape function.
    # shapely allows for shapes with holes in them, but only if the hole touches the outer edge at exactly either 0 or
    # 1 point. So we need to check to make sure that is the case. Ironically, the best way to do that is to convert all
    # the rings to shapely polygons and check whether any of them are not fully enclosed by another.

    if verbose: print(f"Number of closed shapes generated within cluster {k}: {len(rings)}")

    this_cluster = dict()

    for i, ring in enumerate(rings):
        # in order for this to be useful, we now need to associate the indices of the points corresponding to vertices 
        # with the points themselves. Unfortunately, networkx returned the ring vertex indices as a set (and thus unordered)
        # so we first have to order the elements.
        ordered_ring_indices = order_ring(edges, ring)
        ordered_vertices = [(points_in_cluster[i]) for i in ordered_ring_indices]
        # pdb.set_trace()
        # print(np.shape(ordered_vertices))
        # plt.plot(np.asarray(ordered_vertices).T[0], np.asarray(ordered_vertices).T[1])

        polygon = Polygon(ordered_vertices)

        # if plot:
        #     plt.plot(*polygon.exterior.xy)

        this_cluster[i] = {"poly":polygon, "verts":ordered_vertices}

    polygon_goodness = check_polygon_interiority(this_cluster)
    if polygon_goodness[0]:
        return polygon_goodness[1]
    else: 
        #increment epsilon for alpha_shape() and try again
        epsilon_0 += 0.1
        return cluster_to_polygon(points_in_cluster, epsilon_0, k, verbose)


def check_polygon_interiority(polygon_cluster):
    """takes the dictionary of polygon data created in get_shape and returns either 
    (True, reformatted polygon) or (False, None) depending on whether or not one single
    polygon in the set contains every other polygon in the set, where reformatted_polygon
    is a single y:
 143:91   error  pyflakes  invalid syntaxshapely polygon with the other polygons as holes. This is desirable 
    because we know from DBSCAN that this set of points we're looking at SHOULD represent
    a single cluster of observations, and so if we get multiple polygons describing the 
    cluster we know that we set our epsillon too low on the alpha shape generation."""
    n_polys = len(polygon_cluster)
    # pdb.set_trace()
    if n_polys==1:
        return (True, polygon_cluster[0]["poly"])
    else:
        for key, value in polygon_cluster.items():
            contains_all = True #initially assume that the polygon you are looking at does contain
            # every other polygon
            for i in [a for a in range(n_polys) if a != key]:
                if value["poly"].contains(polygon_cluster[i]["poly"]):
                    pass
                else:
                    contains_all = False
                    break
            if contains_all == True: #if at this point 'contains all' is still True, we have a winner
                return (True, Polygon(value["verts"], holes=[polygon_cluster[a]["verts"] for a in range(n_polys) if a != key]))
            else:pass
        return (False, None) #if nothing in that for loop returned True and exited the function, we know that
        # there is no single bounding polygon and our alpha was too low.


def add_poly_to_table(polygon, plant_id):
    """Add a polygon to the DistPoly table"""

    geoalchemy_polygon = geoalchemy2.shape.from_shape(polygon, srid=4326)

    poly = DistPoly(plant_id=plant_id,
                        poly=geoalchemy_polygon)

    # # We need to add to the session or it won't ever be stored
    db.session.add(poly)


def run_all(plot=True):
    global polygon_conversion
    plants_to_cluster = db.engine.execute("SELECT COUNT(DISTINCT plant_id) FROM observations;").scalar()

    ids_to_polygonize = db.engine.execute("SELECT DISTINCT plant_id FROM observations;").fetchall()
    ids_to_polygonize = set(np.asarray(ids_to_polygonize).T[0])

    ids_already_found = db.engine.execute("SELECT DISTINCT plant_id FROM distribution_polygons;").fetchall()
    ids_already_found = set(np.asarray(ids_already_found).T[0])

    # ids_to_polygonize.discard(11566) #it keeps breaking shit and I don't know why

    for plant_id in ids_already_found:
        ids_to_polygonize.discard(plant_id)

    polygon_conversion = tqdm_gui(total=len(ids_to_polygonize), unit="clusters")


    for plant_id in ids_to_polygonize:
        print("\n\n")
        plant_id = int(plant_id)
        obs = Observation.query.filter_by(plant_id=plant_id).all()
        plant_name = Observation.query.filter_by(plant_id=plant_id).first().plant.sci_name
        # plant_id = Observation.query.filter_by(plant_id=4140).first().plant_id
        latlon = np.asarray([[a.lon, a.lat] for a in obs]) 
        added_obs = []

        if len(obs)<100: #arbitrarily pick this as the smallest number of observations 
            # at which we don't need to check in with iNat before proceeding.
            try: added_obs = get_inat_obs(plant_name)
            except Exception: pass
            print("called iNaturalist. Received {} observations.".format((len(added_obs) if added_obs else 0)))
            if added_obs is not None:
                try:
                    latlon = np.vstack((latlon, added_obs))
                except ValueError: pass
            else: pass

        if len(latlon)<=5: #without at least 4 points
            continue #we can deal with these later


        print("\r{0:<5} {1:} observations of {2:>5}: {3:<30}".format(len(latlon), 
            ("({0:<5} from iNaturalist)".format(len(added_obs)) if added_obs else ""), plant_id, plant_name))
        mask_info = dbscan_mask(latlon, verbose=False)
        get_shape(mask_info, latlon, plant_id, plot=False)
        polygon_conversion.update(1)


if __name__ == "__main__":
    run_all()
# plt.title('Estimated number of clusters: %d' % mask_info["n_clusters"])
# plt.show()

