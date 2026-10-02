import sys
from data import load_data, add_new_columns, data_analysis
from clustering import transform_data, kmeans, visualize_results
import numpy as np

def main(argv):
    print("Part A: ")
    df_part_a = load_data('london.csv')
    add_new_columns(df_part_a)
    data_analysis(df_part_a)
    print()
    print("Part B: ")
    df_part_b = load_data('london.csv')
    features = ['cnt', 'hum']
    transformed_data = transform_data(df_part_b, features)
    k_values = [2, 3, 5]
    for k in k_values:
        print()
        labels, centroids = kmeans(transformed_data, k)
        print(f"k = {k}")
        print(np.array_str(centroids, precision=3, suppress_small=True))
        visualize_results(transformed_data, labels, centroids)
        
if __name__ == '__main__':
    main(sys.argv)