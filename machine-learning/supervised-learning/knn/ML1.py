import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score


# Step 1: Generate synthetic samples added seed for each run to make the same output
i=6
def generate_samples(mean, cov, n_samples, label):
    global i
    np.random.seed(i)
    samples = np.random.multivariate_normal(mean, cov, n_samples)
    labels = np.full(n_samples, label)
    i+=1
    return samples, labels


# Gaussian parameters
mu1, mu2, mu3 = [-1, 1], [-2.5, 2.5], [-4.5, 4.5]
sigma = np.eye(2)
num_train_samples = 700

# Generate train samples
samples1, labels1 = generate_samples(mu1, sigma, num_train_samples//3, 0)
samples2, labels2 = generate_samples(mu2, sigma, num_train_samples//3, 1)
samples3, labels3 = generate_samples(mu3, sigma, num_train_samples//3+1, 2)


train_data = np.vstack([samples1, samples2, samples3])
train_labels = np.hstack([labels1, labels2, labels3])


# Step 2: Plot training data
plt.figure(figsize=(8, 6))
plt.scatter(samples1[:, 0], samples1[:, 1], c='red', label='Gaussian 1')
plt.scatter(samples2[:, 0], samples2[:, 1], c='blue', label='Gaussian 2')
plt.scatter(samples3[:, 0], samples3[:, 1], c='green', label='Gaussian 3')
plt.legend()
plt.title("Training Data")
plt.xlabel("x1")
plt.ylabel("x2")
plt.show()

num_test_samples = 300

# Step 3: Generate and plot test samples
samples1_test, labels1_test = generate_samples(mu1, sigma, num_test_samples//3, 0)
samples2_test, labels2_test = generate_samples(mu2, sigma, num_test_samples//3, 1)
samples3_test, labels3_test = generate_samples(mu3, sigma, num_test_samples//3, 2)

test_data = np.vstack([samples1_test, samples2_test, samples3_test])
test_labels = np.hstack([labels1_test, labels2_test, labels3_test])

plt.figure(figsize=(8, 6))
plt.scatter(samples1_test[:, 0], samples1_test[:, 1], c='red', label='Gaussian 1')
plt.scatter(samples2_test[:, 0], samples2_test[:, 1], c='blue', label='Gaussian 2')
plt.scatter(samples3_test[:, 0], samples3_test[:, 1], c='green', label='Gaussian 3')
plt.legend()
plt.title("Test Data")
plt.xlabel("x1")
plt.ylabel("x2")
plt.show()

# Step 4:
knn = KNeighborsClassifier(n_neighbors=1)
knn.fit(train_data, train_labels)

train_preds = knn.predict(train_data)
test_preds = knn.predict(test_data)

#error = 1- accuracy
train_error = 1 - accuracy_score(train_labels, train_preds)
test_error = 1 - accuracy_score(test_labels, test_preds)

print(f"Train Error Rate: {train_error:.4f}")
print(f"Test Error Rate: {test_error:.4f}")

# Step 5: Evaluate for k=1 to 20
k_values = range(1, 21)
train_errors = []
test_errors = []

for k in k_values:
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(train_data, train_labels)
    train_errors.append(1 - accuracy_score(train_labels, knn.predict(train_data)))
    test_errors.append(1 - accuracy_score(test_labels, knn.predict(test_data)))

plt.figure(figsize=(8, 6))
plt.plot(k_values, train_errors, label='Train Error', marker='o')
plt.plot(k_values, test_errors, label='Test Error', marker='o')
plt.xticks(k_values)
plt.legend()
plt.title("Train and Test Error vs. k")
plt.xlabel("k")
plt.ylabel("Error Rate")
plt.show()


# # **counter_example_q1.5**
# # Step 5: Evaluate for k=1 to 700
# k_values = list(range(1, 701, 20))
# k_values.append(700)
# train_errors = []
# test_errors = []
#
# for k in k_values:
#     knn = KNeighborsClassifier(n_neighbors=k)
#     knn.fit(train_data, train_labels)
#     train_errors.append(1 - accuracy_score(train_labels, knn.predict(train_data)))
#     test_errors.append(1 - accuracy_score(test_labels, knn.predict(test_data)))
#
# plt.figure(figsize=(15, 6))
# plt.plot(k_values, train_errors, label='Train Error', marker='o')
# plt.plot(k_values, test_errors, label='Test Error', marker='o')
# plt.xticks(k_values)
# plt.legend()
# plt.title("Train and Test Error vs. k")
# plt.xlabel("k")
# plt.ylabel("Error Rate")
# plt.show()


# Step 6
train_sizes = range(10, 41, 5)
num_test_samples = 100

samples1_test, labels1_test = generate_samples(mu1, sigma, num_test_samples//3, 0)
samples2_test, labels2_test = generate_samples(mu2, sigma, num_test_samples//3, 1)
samples3_test, labels3_test = generate_samples(mu3, sigma, num_test_samples//3+1, 2)

m_test = np.vstack([samples1_test, samples2_test, samples3_test])
m_labels = np.hstack([labels1_test, labels2_test, labels3_test])

for i in range (10):
    train_errors = []
    test_errors = []

    for m_train in train_sizes:
        samples1, labels1 = generate_samples(mu1, sigma, m_train//3, 0)
        samples2, labels2 = generate_samples(mu2, sigma, m_train//3, 1)
        samples3, labels3 = generate_samples(mu3, sigma, m_train//3+1, 2)
        m_train_data = np.vstack([samples1, samples2, samples3])
        m_train_labels = np.hstack([labels1, labels2, labels3])

        knn = KNeighborsClassifier(n_neighbors=10)
        knn.fit(m_train_data, m_train_labels)

        train_errors.append(1 - accuracy_score(m_train_labels, knn.predict(m_train_data)))
        test_errors.append(1 - accuracy_score(m_labels, knn.predict(m_test)))

    plt.figure(figsize=(8, 6))
    plt.plot(train_sizes, train_errors, label='Train Error', marker='o')
    plt.plot(train_sizes, test_errors, label='Test Error', marker='o')
    plt.legend()
    plt.title("Train and Test Error vs. Train Size")
    plt.xlabel("Train Size")
    plt.ylabel("Error Rate")
    plt.show()
