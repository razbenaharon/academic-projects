import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
np.random.seed(2)


def add_noise(data):
    """
    :param data: dataset as numpy array of shape (n, 2)
    :return: data + noise, where noise~N(0,0.001^2)
    """
    noise = np.random.normal(loc=0, scale=0.001, size=data.shape)
    return data + noise


def choose_initial_centroids(data, k):
    """
    :param data: dataset as numpy array of shape (n, 2)
    :param k: number of clusters
    :return: numpy array of k random items from dataset
    """
    n = data.shape[0]
    indices = np.random.choice(range(n), k, replace=False)
    return data[indices]


# ====================
def transform_data(df, features):
    """
    Performs the following transformations on df:
        - selecting relevant features
        - scaling
        - adding noise
    :param df: dataframe as was read from the original csv.
    :param features: list of 2 features from the dataframe
    :return: transformed data as numpy array of shape (n, 2)
    """
    df = df[features]
    n = df.shape[0]
    transformed_data = np.zeros((n, 2))
    for feature in features:
        column_min = df[feature].min()
        column_sum = df[feature].sum()
        df_copy = df.copy()
        df_copy.loc[:, feature] = (df_copy.loc[:, feature] - column_min) / column_sum
        df = df_copy
    transformed_data[:, 0] = df[features[0]].values
    transformed_data[:, 1] = df[features[1]].values
    transformed_data = add_noise(transformed_data)
    return transformed_data


def kmeans(data, k):
    """
    Running kmeans clustering algorithm.
    :param data: numpy array of shape (n, 2)
    :param k: desired number of cluster
    :return:
    * labels - numpy array of size n, where each entry is the predicted label (cluster number)
    * centroids - numpy array of shape (k, 2), centroid for each cluster.
    """
    centroids = choose_initial_centroids(data, k)
    n = 0
    for _ in data:
        n += 1
    labels = np.array([], dtype=int)  # Empty array with integer data type
    labels = np.resize(labels, (n,))
    for i in range(n):
        labels[i] = 0
    prev_centroids = None
    while not np.array_equal(centroids, prev_centroids):
        prev_centroids = centroids.copy()
        labels = assign_to_clusters(data, centroids)
        centroids = recompute_centroids(data, labels, k)
    return labels, centroids


def visualize_results(data, labels, centroids):
    """
    Visualizing results of the kmeans model, and saving the figure.
    :param data: data as numpy array of shape (n, 2)
    :param labels: the final labels of kmeans, as numpy array of size n
    :param centroids: the final centroids of kmeans, as numpy array of shape (k, 2)
    """

    max_val = np.max(labels)
    k = max_val + 1
    colors = ['purple','yellow','red', 'orange', 'pink']
    plt.scatter(data[:, 0], data[:, 1], c=[colors[int(labels)] for labels in labels])
    plt.scatter(centroids[:, 0], centroids[:, 1], color='black', marker='*', label='Centroids')
    plt.title(f'Results for kmeans with k = {k}')
    plt.xlabel('cnt')
    plt.ylabel('hum')
    for i, color in enumerate(colors):
        plt.scatter([], [], color=color, label='Cluster ' + str(i))
    plt.savefig("pic" + f"_k_{k}" + ".PNG")
    plt.show()


def dist(x, y):
    """
    Euclidean distance between vectors x, y
    :param x: numpy array of size n
    :param y: numpy array of size n
    :return: the Euclidean distance
    """
    distance = np.linalg.norm(x - y)
    return distance


def assign_to_clusters(data, centroids):
    """
    Assign each data point to a cluster based on current centroids
    :param data: data as numpy array of shape (n, 2)
    :param centroids: current centroids as numpy array of shape (k, 2)
    :return: numpy array of size n
    """
    n = data.shape[0]
    labels = np.zeros(n)
    for i in range(n):
        distances = np.array([dist(data[i], centroid) for centroid in centroids])
        labels[i] = np.argmin(distances)
    return labels


def recompute_centroids(data, labels, k):
    """
    Recomputes new centroids based on the current assignment
    :param data: data as numpy array of shape (n, 2)
    :param labels: current assignments to clusters for each data point, as numpy array of size n
    :param k: number of clusters
    :return: numpy array of shape (k, 2)
    """
    centroids = np.zeros((k, 2))
    for i in range(k):
        points_of_clusters = data[labels == i]
        if len(points_of_clusters) > 0:
            centroids[i] = np.mean(points_of_clusters, axis=0)
    return centroids
