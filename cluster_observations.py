from model import Observation, Plant, AltName, init_app 
import numpy as np 
# import scipy.spatial.distance as spdist
from flask_sqlalchemy import SQLAlchemy
from sklearn.neighbors import NearestNeighbors

from sklearn.cluster import DBSCAN
from sklearn import metrics
# from sklearn.datasets.samples_generator import make_blobs
# from sklearn.preprocessing import StandardScaler

init_app()
obs = Observation.query.filter_by(plant_id=548).all()
latlon = np.asarray([[a.lat, a.lon] for a in obs])
# pairwise_dists = spdist.pdist(latlon, metric='euclidean')

nn = NearestNeighbors(n_neighbors=2, algorithm='auto', metric='euclidean').fit(latlon)
distances, indices = nn.kneighbors(latlon, return_distance=True)
allowed_dist = np.mean(distances[:,1]) + 7*np.std(distances[:,1])
# #############################################################################
# Compute DBSCAN
db = DBSCAN(eps=0.3, min_samples=10).fit(latlon) #previously eps=allowed_dist, but about 0.3 seems to give the best results anyway
core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
core_samples_mask[db.core_sample_indices_] = True
labels = db.labels_
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
n_noise_ = list(labels).count(-1)

# print("Epsillon: %0.3f" % allowed_dist)
print('Estimated number of clusters: %d' % n_clusters_)
print('Estimated number of noise points: %d' % n_noise_)
print("Silhouette Coefficient: %0.3f" % metrics.silhouette_score(latlon, labels))

# #############################################################################
# Plot result
import matplotlib.pyplot as plt

# Black removed and is used for noise instead.
unique_labels = set(labels)
colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]

for k, col in zip(unique_labels, colors):
    if k == -1:
        # Black used for noise.
        col = [0, 0, 0, 0]
    class_member_mask = (labels == k)
    xy = latlon[class_member_mask & core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col), markeredgecolor='k', markersize=14)
    xy = latlon[class_member_mask & ~core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col), markeredgecolor='k', markersize=6)

plt.title('Estimated number of clusters: %d' % n_clusters_)
plt.show()
