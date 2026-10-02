import os
import sys
import argparse
import time
import itertools
import numpy as np
import pandas as pd
from collections import Counter



class KnnClassifier:
    def __init__(self, k: int, p: float):
        """
        Constructor for the KnnClassifier.

        :param k: Number of nearest neighbors to use.
        :param p: p parameter for Minkowski distance calculation.
        """
        self.k = k
        self.p = p

        # TODO - Place your student IDs here. Single submitters please use a tuple like so: self.ids = (000000000,)
        self.ids = (000000000, 000000000)

        # Save X and y
        self.trainX = None
        self.trainY = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        This method trains a k-NN classifier on a given training set X with label set y.

        :param X: A 2-dimensional numpy array of m rows and d columns. It is guaranteed that m >= 1 and d >= 1.
            Array datatype is guaranteed to be np.float32.
        :param y: A 1-dimensional numpy array of m rows. it is guaranteed to match X's rows in length (|m_x| == |m_y|).
            Array datatype is guaranteed to be np.uint8.
        """

        self.trainX = X
        self.trainY = y

        pass

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        This method predicts the y labels of a given dataset X, based on a previous training of the model.
        It is mandatory to call KnnClassifier.fit before calling this method.

        :param X: A 2-dimensional numpy array of m rows and d columns. It is guaranteed that m >= 1 and d >= 1.
            Array datatype is guaranteed to be np.float32.
        :return: A 1-dimensional numpy array of m rows. Should be of datatype np.uint8.
        """

        predictions = []

        trainX_expanded = self.trainX[:, np.newaxis, :]

        testX_expanded = X[np.newaxis, :, :]

        squared_diff = (trainX_expanded - testX_expanded) ** self.p

        sum_squared_diff = np.sum(squared_diff, axis=2)

        distances = np.power(sum_squared_diff, 1 / self.p)

        for i in range(distances.shape[1]):  # Loop over each test sample
            # Get the indices of the sorted distances (ascending order)
            sorted_indices = np.argsort(distances[:, i])  # Indices of the sorted distances
            sorted_distances = distances[sorted_indices, i]  # Sorted distances for the test point
            sorted_labels = self.trainY[sorted_indices]  # Corresponding labels of the sorted neighbors

            if (self.k<distances.shape[1]):
                if (sorted_distances[self.k])==(sorted_distances[self.k+1]):
                    k_label= sorted_labels[self.k]
                    kplus_label= sorted_labels[self.k+1]
                    if kplus_label < k_label:
                        sorted_labels[self.k] = sorted_labels[self.k + 1]


            nearest_labels = sorted_labels[:self.k]
            nearest_distances = sorted_distances[:self.k]

            count = Counter(nearest_labels)

            if len(count) == 1:
                predicted_label = list(count.keys())[0]
            else:
                max_count = max(count.values())
                tied_classes = [label for label, c in count.items() if c == max_count]

                if len(tied_classes) > 1:
                    nearest_label = nearest_labels[0]
                    nearest_distance = nearest_distances[0]


                    for label in tied_classes:
                        tied_label_indices = np.where(np.array(nearest_labels) == label)[0]
                        tied_distances = np.array(nearest_distances)[tied_label_indices]

                        if min(tied_distances) < nearest_distance:
                            nearest_label = label
                            nearest_distance = min(tied_distances)

                    predicted_label = nearest_label
                else:
                    predicted_label = tied_classes[0]


            predictions.append(predicted_label)

        return np.array(predictions, dtype=np.uint8)



def main():

    print("*" * 20)
    print("Started HW1_000000000_000000000.py")
    # Parsing script arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('csv', type=str, help='Input csv file path')
    parser.add_argument('k', type=int, help='k parameter')
    parser.add_argument('p', type=float, help='p parameter')
    args = parser.parse_args()

    print("Processed input arguments:")
    print(f"csv = {args.csv}, k = {args.k}, p = {args.p}")

    print("Initiating KnnClassifier")
    model = KnnClassifier(k=args.k, p=args.p)
    print(f"Student IDs: {model.ids}")
    print(f"Loading data from {args.csv}...")
    data = pd.read_csv(args.csv, header=None)
    print(f"Loaded {data.shape[0]} rows and {data.shape[1]} columns")
    X = data[data.columns[:-1]].values.astype(np.float32)
    y = pd.factorize(data[data.columns[-1]])[0].astype(np.uint8)
    print("Fitting...")
    model.fit(X, y)
    print("Done")
    print("Predicting...")
    y_pred = model.predict(X)
    print("Done")
    accuracy = np.sum(y_pred == y) / len(y)
    print(f"Train accuracy: {accuracy * 100 :.2f}%")
    print("*" * 20)


if __name__ == "__main__":
    main()
