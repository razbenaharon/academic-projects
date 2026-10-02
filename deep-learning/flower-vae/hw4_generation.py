import torch
import torch.nn as nn
from torchvision import transforms
import matplotlib.pyplot as plt
import json
import os
import numpy as np
from hw4_code import VAE, FlowerDataset


def reproduce_hw4(model_path='hw4_model.pkl', 
                  category_json='category_to_images.json',
                  images_dir='jpg',
                  output_dir='generated_outputs',
                  latent_dim=256,
                  device='cuda'):
    """
    Load trained model and generate 10 images from each class
    
    Args:
        model_path: Path to saved model weights
        category_json: Path to category_to_images.json
        images_dir: Directory containing flower images
        output_dir: Directory to save generated images
        latent_dim: Latent dimension used in the model
        device: Device to run on
    """
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Set device
    device = torch.device(device if torch.cuda.is_available() else 'cpu')
    print(f'Using device: {device}')
    
    # Load the model
    print("Loading model...")
    model = VAE(latent_dim=latent_dim, image_channels=3)
    state = torch.load(model_path, map_location=device, weights_only=True)
    checkpoint_dim = state["fc_mu.weight"].shape[0]
    if checkpoint_dim != latent_dim:
        raise ValueError(f"Checkpoint latent dimension is {checkpoint_dim}; pass latent_dim={checkpoint_dim}")
    model.load_state_dict(state)
    model = model.to(device)
    model.eval()
    print("Model loaded successfully!")
    
    # Load category information
    with open(category_json, 'r') as f:
        category_to_images = json.load(f)
    
    num_classes = len(category_to_images)
    print(f'Number of classes: {num_classes}')
    
    # Load dataset to get class-conditioned latent vectors
    transform = transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.ToTensor(),
    ])
    
    dataset = FlowerDataset(images_dir, category_json, transform=transform)
    
    # Get representative latent vectors for each class
    print("Computing class-representative latent vectors...")
    class_latent_vectors = {}
    
    # Organize dataset by class
    class_to_indices = {}
    for idx, label in enumerate(dataset.labels):
        if label not in class_to_indices:
            class_to_indices[label] = []
        class_to_indices[label].append(idx)
    
    with torch.no_grad():
        for class_label, indices in class_to_indices.items():
            # Sample a few images from this class and get their latent vectors
            sample_indices = np.random.choice(indices, min(5, len(indices)), replace=False)
            latent_vectors = []
            
            for idx in sample_indices:
                image, _ = dataset[idx]
                image = image.unsqueeze(0).to(device)
                mu, logvar = model.encode(image)
                latent_vectors.append(mu.cpu().numpy())
            
            # Average latent vector for this class
            avg_latent = np.mean(latent_vectors, axis=0)
            class_latent_vectors[class_label] = avg_latent
    
    # Generate 10 images for each class
    print("Generating images for each class...")
    
    all_generated_images = []
    all_class_labels = []
    
    with torch.no_grad():
        for class_label in sorted(class_latent_vectors.keys()):
            # Get the average latent vector for this class
            base_latent = class_latent_vectors[class_label]
            
            # Generate 10 variations by adding small random noise
            generated_images = []
            for i in range(10):
                # Add controlled noise to create variation
                noise = np.random.randn(latent_dim) * 0.3
                z = torch.as_tensor(base_latent + noise, dtype=torch.float32, device=device).reshape(1, latent_dim)
                
                # Generate image
                generated = model.decode(z).cpu()
                generated_images.append(generated[0])
            
            all_generated_images.extend(generated_images)
            all_class_labels.extend([class_label] * 10)
            
            # Save images for this class
            class_output_path = os.path.join(output_dir, f'class_{class_label+1:03d}.png')
            fig, axes = plt.subplots(2, 5, figsize=(15, 6))
            axes = axes.flatten()
            
            for i, img_tensor in enumerate(generated_images):
                img = img_tensor.permute(1, 2, 0).numpy()
                axes[i].imshow(img)
                axes[i].axis('off')
                axes[i].set_title(f'Sample {i+1}')
            
            plt.suptitle(f'Class {class_label+1} - Generated Images', fontsize=16)
            plt.tight_layout()
            plt.savefig(class_output_path, dpi=200, bbox_inches='tight')
            plt.close()
            
            print(f'Class {class_label+1}: Generated 10 images -> {class_output_path}')
    
    # Create a summary visualization (first 20 classes)
    print("Creating summary visualization...")
    n_classes_to_show = min(20, num_classes)
    fig, axes = plt.subplots(n_classes_to_show, 10, figsize=(20, 2*n_classes_to_show))
    
    for class_idx in range(n_classes_to_show):
        start_idx = class_idx * 10
        for img_idx in range(10):
            img = all_generated_images[start_idx + img_idx].permute(1, 2, 0).numpy()
            axes[class_idx, img_idx].imshow(img)
            axes[class_idx, img_idx].axis('off')
        
        axes[class_idx, 0].set_ylabel(f'Class {class_idx+1}', fontsize=10, rotation=0, 
                                      ha='right', va='center')
    
    plt.suptitle('Generated Images Summary (First 20 Classes)', fontsize=16)
    plt.tight_layout()
    summary_path = os.path.join(output_dir, 'summary_all_classes.png')
    plt.savefig(summary_path, dpi=200, bbox_inches='tight')
    plt.close()
    
    print(f"Summary visualization saved to {summary_path}")
    print(f"\nGeneration complete! Total images generated: {len(all_generated_images)}")
    print(f"Output directory: {output_dir}")
    
    return all_generated_images, all_class_labels


if __name__ == '__main__':
    # Run the reproduction function
    reproduce_hw4(
        model_path='hw4_model.pkl',
        category_json='category_to_images.json',
        images_dir='jpg',
        output_dir='generated_outputs',
        latent_dim=256,
        device='cuda' if torch.cuda.is_available() else 'cpu'
    )
