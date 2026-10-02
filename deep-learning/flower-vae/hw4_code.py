import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import json
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
import tarfile
from pathlib import Path


class FlowerDataset(Dataset):
    """Dataset class for 102 Category Flower Dataset"""
    
    def __init__(self, root_dir, category_json_path, transform=None):
        """
        Args:
            root_dir: Directory with extracted flower images
            category_json_path: Path to category_to_images.json
            transform: Optional transform to be applied on images
        """
        self.root_dir = root_dir
        self.transform = transform
        
        # Load category mappings
        with open(category_json_path, 'r') as f:
            self.category_to_images = json.load(f)
        
        # Create image list with labels
        self.images = []
        self.labels = []
        
        for category, image_list in self.category_to_images.items():
            category_idx = int(category) - 1  # Convert to 0-indexed
            for img_name in image_list:
                self.images.append(img_name)
                self.labels.append(category_idx)
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        img_name = self.images[idx]
        img_path = os.path.join(self.root_dir, img_name)
        
        try:
            image = Image.open(img_path).convert('RGB')
        except:
            # Handle corrupted images
            print(f"Warning: Could not load {img_path}")
            image = Image.new('RGB', (128, 128), color='white')
        
        label = self.labels[idx]
        
        if self.transform:
            image = self.transform(image)
        
        return image, label


class VAE(nn.Module):
    """Variational Autoencoder for flower images"""
    
    def __init__(self, latent_dim=128, image_channels=3):
        super(VAE, self).__init__()
        
        self.latent_dim = latent_dim
        
        # Encoder
        # Input: 3 x 128 x 128
        self.encoder = nn.Sequential(
            nn.Conv2d(image_channels, 32, kernel_size=4, stride=2, padding=1),  # 32 x 64 x 64
            nn.BatchNorm2d(32),
            nn.LeakyReLU(0.2),
            
            nn.Conv2d(32, 64, kernel_size=4, stride=2, padding=1),  # 64 x 32 x 32
            nn.BatchNorm2d(64),
            nn.LeakyReLU(0.2),
            
            nn.Conv2d(64, 128, kernel_size=4, stride=2, padding=1),  # 128 x 16 x 16
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2),
            
            nn.Conv2d(128, 256, kernel_size=4, stride=2, padding=1),  # 256 x 8 x 8
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2),
            
            nn.Conv2d(256, 512, kernel_size=4, stride=2, padding=1),  # 512 x 4 x 4
            nn.BatchNorm2d(512),
            nn.LeakyReLU(0.2),
        )
        
        # Latent space
        self.fc_mu = nn.Linear(512 * 4 * 4, latent_dim)
        self.fc_logvar = nn.Linear(512 * 4 * 4, latent_dim)
        
        # Decoder input
        self.decoder_input = nn.Linear(latent_dim, 512 * 4 * 4)
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(512, 256, kernel_size=4, stride=2, padding=1),  # 256 x 8 x 8
            nn.BatchNorm2d(256),
            nn.ReLU(),
            
            nn.ConvTranspose2d(256, 128, kernel_size=4, stride=2, padding=1),  # 128 x 16 x 16
            nn.BatchNorm2d(128),
            nn.ReLU(),
            
            nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1),  # 64 x 32 x 32
            nn.BatchNorm2d(64),
            nn.ReLU(),
            
            nn.ConvTranspose2d(64, 32, kernel_size=4, stride=2, padding=1),  # 32 x 64 x 64
            nn.BatchNorm2d(32),
            nn.ReLU(),
            
            nn.ConvTranspose2d(32, image_channels, kernel_size=4, stride=2, padding=1),  # 3 x 128 x 128
            nn.Sigmoid()
        )
    
    def encode(self, x):
        """Encode input to latent space"""
        h = self.encoder(x)
        h = h.view(h.size(0), -1)
        mu = self.fc_mu(h)
        logvar = self.fc_logvar(h)
        return mu, logvar
    
    def reparameterize(self, mu, logvar):
        """Reparameterization trick"""
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std
    
    def decode(self, z):
        """Decode latent vector to image"""
        h = self.decoder_input(z)
        h = h.view(h.size(0), 512, 4, 4)
        return self.decoder(h)
    
    def forward(self, x):
        """Forward pass through VAE"""
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        recon = self.decode(z)
        return recon, mu, logvar


def vae_loss(recon_x, x, mu, logvar, beta=1.0):
    """
    VAE loss function: reconstruction loss + KL divergence
    
    Args:
        recon_x: Reconstructed images
        x: Original images
        mu: Mean of latent distribution
        logvar: Log variance of latent distribution
        beta: Weight for KL divergence (beta-VAE)
    
    Returns:
        total_loss, recon_loss, kl_loss
    """
    # Reconstruction loss (Binary Cross Entropy)
    recon_loss = F.binary_cross_entropy(recon_x, x, reduction='sum')
    
    # KL divergence
    # -0.5 * sum(1 + log(sigma^2) - mu^2 - sigma^2)
    kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    
    # Total loss
    total_loss = recon_loss + beta * kl_loss
    
    return total_loss, recon_loss, kl_loss


def train_vae(model, train_loader, num_epochs=100, learning_rate=1e-3, 
              beta=1.0, device='cuda', save_path='hw4_model.pkl'):
    """
    Train the VAE model
    
    Args:
        model: VAE model
        train_loader: DataLoader for training data
        num_epochs: Number of training epochs
        learning_rate: Learning rate for optimizer
        beta: Weight for KL divergence
        device: Device to train on
        save_path: Path to save the trained model
    
    Returns:
        Dictionary containing loss histories
    """
    model = model.to(device)
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    # Learning rate scheduler
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=5
    )
    
    # Loss histories
    history = {
        'total_loss': [],
        'recon_loss': [],
        'kl_loss': []
    }
    
    model.train()
    
    for epoch in range(num_epochs):
        epoch_total_loss = 0
        epoch_recon_loss = 0
        epoch_kl_loss = 0
        
        for batch_idx, (data, _) in enumerate(train_loader):
            data = data.to(device)
            
            optimizer.zero_grad()
            
            # Forward pass
            recon_batch, mu, logvar = model(data)
            
            # Calculate loss
            total_loss, recon_loss, kl_loss = vae_loss(
                recon_batch, data, mu, logvar, beta
            )
            
            # Backward pass
            total_loss.backward()
            optimizer.step()
            
            # Accumulate losses
            epoch_total_loss += total_loss.item()
            epoch_recon_loss += recon_loss.item()
            epoch_kl_loss += kl_loss.item()
        
        # Average losses
        avg_total_loss = epoch_total_loss / len(train_loader.dataset)
        avg_recon_loss = epoch_recon_loss / len(train_loader.dataset)
        avg_kl_loss = epoch_kl_loss / len(train_loader.dataset)
        
        # Store history
        history['total_loss'].append(avg_total_loss)
        history['recon_loss'].append(avg_recon_loss)
        history['kl_loss'].append(avg_kl_loss)
        
        # Update learning rate
        scheduler.step(avg_total_loss)
        
        # Print progress
        if (epoch + 1) % 5 == 0:
            print(f'Epoch [{epoch+1}/{num_epochs}] '
                  f'Total Loss: {avg_total_loss:.4f} '
                  f'Recon Loss: {avg_recon_loss:.4f} '
                  f'KL Loss: {avg_kl_loss:.4f}')
    
    # Save model
    torch.save(model.state_dict(), save_path)
    print(f'Model saved to {save_path}')
    
    return history


def plot_training_curves(history, save_path='training_curves.png'):
    """Plot training loss curves"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    # Total loss
    axes[0].plot(history['total_loss'])
    axes[0].set_title('Total Loss')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].grid(True)
    
    # Reconstruction loss
    axes[1].plot(history['recon_loss'])
    axes[1].set_title('Reconstruction Loss')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Loss')
    axes[1].grid(True)
    
    # KL divergence
    axes[2].plot(history['kl_loss'])
    axes[2].set_title('KL Divergence')
    axes[2].set_xlabel('Epoch')
    axes[2].set_ylabel('Loss')
    axes[2].grid(True)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'Training curves saved to {save_path}')


def generate_images(model, num_images=10, latent_dim=128, device='cuda', 
                   save_path='generated_images.png'):
    """Generate images by sampling from latent space"""
    model.eval()
    
    with torch.no_grad():
        # Sample random latent vectors
        z = torch.randn(num_images, latent_dim).to(device)
        
        # Generate images
        generated = model.decode(z).cpu()
    
    # Plot generated images
    fig, axes = plt.subplots(2, 5, figsize=(15, 6))
    axes = axes.flatten()
    
    for i in range(num_images):
        img = generated[i].permute(1, 2, 0).numpy()
        axes[i].imshow(img)
        axes[i].axis('off')
        axes[i].set_title(f'Generated {i+1}')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'Generated images saved to {save_path}')
    
    return generated


def plot_embeddings(embeddings, labels, save_path='latent_space.png'):
    """
    Visualize latent space using t-SNE
    
    Args:
        embeddings: Latent representations (n_samples, latent_dim)
        labels: Class labels (n_samples,)
        save_path: Path to save the plot
    """
    # Apply t-SNE for dimensionality reduction
    tsne = TSNE(n_components=2, random_state=42, perplexity=30)
    embeddings_2d = tsne.fit_transform(embeddings)
    
    # Plot
    plt.figure(figsize=(12, 10))
    
    # Get unique classes
    unique_labels = np.unique(labels)
    n_classes = len(unique_labels)
    
    # Use colormap
    colors = plt.cm.tab20(np.linspace(0, 1, min(n_classes, 20)))
    if n_classes > 20:
        colors = plt.cm.viridis(np.linspace(0, 1, n_classes))
    
    # Plot each class
    for idx, label in enumerate(unique_labels):
        mask = labels == label
        plt.scatter(embeddings_2d[mask, 0], embeddings_2d[mask, 1], 
                   c=[colors[idx % len(colors)]], 
                   label=f'Class {label+1}', 
                   alpha=0.6, s=20)
    
    plt.xlabel('t-SNE Dimension 1')
    plt.ylabel('t-SNE Dimension 2')
    plt.title('Latent Space Visualization (t-SNE)')
    
    # Create legend with multiple columns if many classes
    if n_classes > 20:
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', ncol=2, fontsize=8)
    else:
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'Latent space visualization saved to {save_path}')


def visualize_latent_space(model, dataset, num_samples_per_class=20, 
                          device='cuda', save_path='latent_space.png'):
    """
    Visualize latent space by encoding samples from each class
    
    Args:
        model: Trained VAE model
        dataset: FlowerDataset instance
        num_samples_per_class: Number of samples to use per class
        device: Device to run on
        save_path: Path to save visualization
    """
    model.eval()
    
    # Organize samples by class
    class_to_indices = {}
    for idx, label in enumerate(dataset.labels):
        if label not in class_to_indices:
            class_to_indices[label] = []
        class_to_indices[label].append(idx)
    
    all_embeddings = []
    all_labels = []
    
    with torch.no_grad():
        for label, indices in class_to_indices.items():
            # Sample up to num_samples_per_class images from this class
            sampled_indices = np.random.choice(
                indices, 
                min(num_samples_per_class, len(indices)), 
                replace=False
            )
            
            for idx in sampled_indices:
                image, _ = dataset[idx]
                image = image.unsqueeze(0).to(device)
                
                # Encode image (use mu, not sampled z)
                mu, _ = model.encode(image)
                
                all_embeddings.append(mu.cpu().numpy())
                all_labels.append(label)
    
    # Convert to numpy arrays
    embeddings = np.vstack(all_embeddings)
    labels = np.array(all_labels)
    
    # Plot embeddings
    plot_embeddings(embeddings, labels, save_path)
    
    return embeddings, labels


def extract_flowers_dataset(tgz_path, extract_to='./'):
    """Extract the 102flowers.tgz file"""
    print(f"Extracting {tgz_path}...")
    with tarfile.open(tgz_path, 'r:gz') as tar:
        tar.extractall(path=extract_to)
    print("Extraction complete!")
    
    # Find the extracted directory
    extracted_dir = os.path.join(extract_to, 'jpg')
    if os.path.exists(extracted_dir):
        return extracted_dir
    else:
        # Try to find it
        for root, dirs, files in os.walk(extract_to):
            if 'jpg' in dirs:
                return os.path.join(root, 'jpg')
    return None


def main(epochs=200, batch_size=32, learning_rate=1e-3, latent_dim=256, beta=0.5, image_size=128):
    """Main training pipeline"""
    
    # Hyperparameters
    LATENT_DIM = latent_dim
    BATCH_SIZE = batch_size
    NUM_EPOCHS = epochs
    LEARNING_RATE = learning_rate
    BETA = beta
    IMAGE_SIZE = image_size
    
    # Paths
    TGZ_PATH = '102flowers.tgz'  # Update this path
    CATEGORY_JSON = 'category_to_images.json'  # Update this path
    
    # Device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Using device: {device}')
    
    # Extract dataset if needed
    if os.path.exists('jpg') and os.path.isdir('jpg'):
        print("Dataset directory 'jpg' found. Skipping extraction.")
        IMAGES_DIR = 'jpg'
    elif os.path.exists(TGZ_PATH):
        extract_dir = extract_flowers_dataset(TGZ_PATH, extract_to='./')
        IMAGES_DIR = extract_dir
    else:
        IMAGES_DIR = 'jpg'  # Assume already extracted
    
    # Data transforms
    transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
    ])
    
    # Create dataset and dataloader
    print("Loading dataset...")
    dataset = FlowerDataset(IMAGES_DIR, CATEGORY_JSON, transform=transform)
    train_loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, 
                             num_workers=4, pin_memory=True)
    
    print(f'Dataset size: {len(dataset)} images')
    print(f'Number of classes: {len(set(dataset.labels))}')
    
    # Create model
    print("Creating VAE model...")
    model = VAE(latent_dim=LATENT_DIM, image_channels=3)
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    print(f'Total parameters: {total_params:,}')
    
    # Train model
    print("Starting training...")
    history = train_vae(
        model, train_loader, 
        num_epochs=NUM_EPOCHS, 
        learning_rate=LEARNING_RATE,
        beta=BETA,
        device=device,
        save_path='hw4_model.pkl'
    )
    
    # Plot training curves
    plot_training_curves(history, save_path='training_curves.png')
    
    # Generate images
    print("Generating images...")
    generate_images(model, num_images=10, latent_dim=LATENT_DIM, 
                   device=device, save_path='generated_images.png')
    
    # Visualize latent space
    print("Visualizing latent space...")
    visualize_latent_space(model, dataset, num_samples_per_class=20,
                          device=device, save_path='latent_space.png')
    
    print("Training complete!")


if __name__ == '__main__':
    main()
