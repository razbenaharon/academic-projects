from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, udf
from pyspark.sql.types import DoubleType, ArrayType, StructType, StructField
from pyspark.ml.linalg import Vectors
from pyspark.ml.feature import VectorAssembler
from pyspark import SparkContext


def euclidean_distance(v1, v2):
    return float(sum((a - b) ** 2 for a, b in zip(v1, v2)) ** 0.5)

def kmeans_fit(data: DataFrame,
               init: DataFrame,
               k: int = 4,
               max_iter: int = 10):

    centroids = [Vectors.dense(row['_1'], row['_2'], row['_3']) for row in init.collect()]
    centroids_broadcast = sc.broadcast(centroids)
    assembler = VectorAssembler(inputCols=['_1', '_2', '_3'], outputCol='features')
    data = assembler.transform(data)

    for iteration in range(max_iter):
      def assign_cluster(features):
            centroids = centroids_broadcast.value
            distances = [euclidean_distance(features.toArray(), centroid.toArray()) for centroid in centroids]
            return float(distances.index(min(distances)))

      assign_cluster_udf = udf(assign_cluster, DoubleType())
      data_with_clusters = data.withColumn('cluster', assign_cluster_udf(col('features')))
      new_centroids = data_with_clusters.groupBy('cluster').agg({'_1': 'avg', '_2': 'avg', '_3': 'avg'})
      new_centroids_rdd = new_centroids.rdd.map(lambda row: Vectors.dense(row['avg(_1)'], row['avg(_2)'], row['avg(_3)']))
      new_centroids_vector = new_centroids_rdd.collect()
      num_converged = 0

      for new_centroid in new_centroids_vector:
          min_distance = min(euclidean_distance(new_centroid, old_centroid) for old_centroid in centroids_broadcast.value)
          if min_distance < 0.001:
            num_converged += 1

      if num_converged == k:
        centroids = new_centroids_vector
        centroids_broadcast = sc.broadcast(centroids)
        break

      centroids = new_centroids_vector
      centroids_broadcast = sc.broadcast(centroids)

    schema = StructType([StructField("centroids", ArrayType(DoubleType()), False)])
    final_centroids_df = spark.createDataFrame(
        [(list(map(float, centroid.toArray())),) for centroid in centroids],
        schema=schema
    )

    return final_centroids_df
    pass
