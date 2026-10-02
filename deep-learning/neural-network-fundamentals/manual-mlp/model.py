"""Manual sigmoid/tanh MLP and gradients, extracted from the original coursework.
Uses PyTorch tensor operations; no autograd in training.
"""
import torch

def sigmoid(x):
    return 1 / (1 + torch.exp(-x))

def tanh(x):
    # Avoid inf/inf from the direct exponential quotient at large magnitudes.
    return 2 * sigmoid(2 * x) - 1


def softmax(x):
    exp_x = torch.exp(x.T - torch.max(x, dim=-1).values).T  # Subtracting max(x) for numerical stability
    return exp_x / exp_x.sum(dim=-1, keepdim=True)

def d_sigmoid(x):
    s = 1 / (1 + torch.exp(-x))
    return s * (1 - s)


def d_tanh(x):
    t = tanh(x)
    return 1 - t**2


def d_softmax(x):
    # using the derivation rule above. using matrix to save previos calculated components
    s = softmax(x)
    jacobian = torch.zeros(s.size() + s.size()[-1:])
    for i in range(s.size()[-1]):
        for k in range(s.size()[-1]):
            if i == k:
                jacobian[..., i, k] = s[..., i] * (1 - s[..., k])
            else:
                jacobian[..., i, k] = -s[..., i] * s[..., k]
    return jacobian

def one_hot(y, num_of_classes=10):
    hot = torch.zeros((y.shape[0], num_of_classes), device=y.device)
    hot[torch.arange(y.shape[0], device=y.device), y] = 1
    return hot


def cross_entropy(y, y_hat):
    return -torch.sum(one_hot(y, y_hat.shape[1]) * torch.log(y_hat.clamp_min(torch.finfo(y_hat.dtype).tiny))) / y.shape[0]


class FullyConnectedNetwork:
    def __init__(self, input_size, output_size, hidden_size1, activiation_func, lr=0.01):
        # parameters
        self.input_size = input_size
        self.output_size = output_size
        self.hidden_size1 = hidden_size1

        # activation function
        self.activation_func = activiation_func
        if activiation_func is sigmoid:
            self.d_activation_func = d_sigmoid
        elif activiation_func is tanh:
            self.d_activation_func = d_tanh
        else:
            raise ValueError("Hidden activation must be this module's sigmoid or tanh")
        limit1 = (6 / (input_size + hidden_size1))**0.5
        self.W1 = torch.empty(self.input_size, self.hidden_size1).uniform_(-limit1, limit1)
        self.b1 = torch.zeros(self.hidden_size1)

        limit2 = (6 / (hidden_size1 + output_size))**0.5
        self.W2 = torch.empty(self.hidden_size1, self.output_size).uniform_(-limit2, limit2)
        self.b2 = torch.zeros(self.output_size)

        self.lr = lr

    def forward(self, x):
        self.x = x

        # === Layer 1: Hidden Layer ===
        self.Z1 = x @ self.W1 + self.b1
        self.A1 = self.activation_func(self.Z1)
        # === Layer 2: Output Layer ===
        self.Z2 = self.A1 @ self.W2 + self.b2

        # Output activation (Softmax)
        self.y_hat = softmax(self.Z2)

        return self.y_hat


    def backward(self, x, y, y_hat):
        y_one_hot = one_hot(y, num_of_classes=self.output_size)
        dZ2 = (y_hat - y_one_hot) / x.size(0)
        dW2 = self.A1.T @ dZ2
        db2 = torch.sum(dZ2, dim=0)
        dA1 = dZ2 @ self.W2.T
        d_act = self.d_activation_func(self.Z1)
        dZ1 = dA1 * d_act
        dW1 = x.T @ dZ1
        db1 = torch.sum(dZ1, dim=0)

        # --- Parameter Update (Gradient Descent) ---

        self.W2 -= self.lr * dW2
        self.b2 -= self.lr * db2
        self.W1 -= self.lr * dW1
        self.b1 -= self.lr * db1
