import torch.nn as nn

class CompactCatCNN_v2(nn.Module):
    """CompactCatCNN_v2 - 2.36M parameters

    Key feature: 256 channels in conv4 (instead of 512)
    17% fewer parameters than v1 for better competitive score
    """
    def __init__(self, num_classes=10):
        super(CompactCatCNN_v2, self).__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(3, 64, 3, 1, 1), nn.BatchNorm2d(64), nn.ReLU(True),
            nn.Conv2d(64, 64, 3, 1, 1), nn.BatchNorm2d(64), nn.ReLU(True),
            nn.MaxPool2d(2, 2), nn.Dropout2d(0.25))
        self.conv2 = nn.Sequential(
            nn.Conv2d(64, 128, 3, 1, 1), nn.BatchNorm2d(128), nn.ReLU(True),
            nn.Conv2d(128, 128, 3, 1, 1), nn.BatchNorm2d(128), nn.ReLU(True),
            nn.MaxPool2d(2, 2), nn.Dropout2d(0.25))
        self.conv3 = nn.Sequential(
            nn.Conv2d(128, 256, 3, 1, 1), nn.BatchNorm2d(256), nn.ReLU(True),
            nn.Conv2d(256, 256, 3, 1, 1), nn.BatchNorm2d(256), nn.ReLU(True),
            nn.MaxPool2d(2, 2), nn.Dropout2d(0.3))
        self.conv4 = nn.Sequential(
            nn.Conv2d(256, 256, 3, 1, 1), nn.BatchNorm2d(256), nn.ReLU(True),  # 256 channels
            nn.Conv2d(256, 256, 3, 1, 1), nn.BatchNorm2d(256), nn.ReLU(True),
            nn.MaxPool2d(2, 2), nn.Dropout2d(0.3))
        self.global_avg_pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Sequential(
            nn.Flatten(), nn.Linear(256, 128), nn.BatchNorm1d(128),
            nn.ReLU(True), nn.Dropout(0.5), nn.Linear(128, num_classes))

    def forward(self, x):
        return self.fc(self.global_avg_pool(self.conv4(self.conv3(self.conv2(self.conv1(x))))))
