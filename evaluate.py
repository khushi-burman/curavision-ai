import torch
from torch.utils.data import DataLoader
import timm
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd
import numpy as np

from dataset import HAM10000Dataset, val_transforms

def evaluate():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    # 1. Load Test Dataset
    test_dataset = HAM10000Dataset(csv_file='data/test.csv', root_dir='data', transform=val_transforms)
    test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False, num_workers=0)

    # 2. Rebuild Model Architecture & Load Saved Checkpoint
    print("Loading model structure and saved weights...")
    model = timm.create_model('efficientnet_b4', pretrained=False, num_classes=7)
    model.load_state_dict(torch.load('best_skin_model.pth', map_location=device))
    model = model.to(device)
    model.eval()

    # 3. Predict on Test Data
    all_preds = []
    all_labels = []

    print("Running evaluation on test dataset...")
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            outputs = model(images)
            preds = outputs.argmax(dim=1)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.numpy())

    # 4. Display Metrics
    print("\n" + "="*50)
    print("                EVALUATION REPORT")
    print("="*50 + "\n")

    print("Classification Report:")
    print(classification_report(all_labels, all_preds, digits=4))

    print("\nConfusion Matrix:")
    print(confusion_matrix(all_labels, all_preds))

if __name__ == '__main__':
    evaluate()