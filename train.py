import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import timm
from dataset import HAM10000Dataset, train_transforms, val_transforms

def main():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    # 1. Load Datasets
    train_dataset = HAM10000Dataset(csv_file='data/train.csv', root_dir='data', transform=train_transforms)
    val_dataset = HAM10000Dataset(csv_file='data/val.csv', root_dir='data', transform=val_transforms)

    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False, num_workers=0)

    # 2. Build EfficientNet-B4 Model
    print("Loading EfficientNet-B4 pre-trained model...")
    model = timm.create_model('efficientnet_b4', pretrained=True, num_classes=7)

    # Load existing checkpoint if present
    if os.path.exists('best_skin_model.pth'):
        print("--> Found existing checkpoint 'best_skin_model.pth'. Loading trained weights...")
        model.load_state_dict(torch.load('best_skin_model.pth', map_location=device))

    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-2)

    # 3. Training Loop (Fine-tuning for 2-3 additional epochs)
    epochs = 3
    best_val_loss = float('inf')

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for step, (images, labels) in enumerate(train_loader):
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            if (step + 1) % 50 == 0:
                print(f"Epoch [{epoch+1}/{epochs}] | Step [{step+1}/{len(train_loader)}] | Loss: {loss.item():.4f}")

        # Validation Phase
        model.eval()
        val_loss = 0.0
        correct = 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                val_loss += loss.item() * images.size(0)
                preds = outputs.argmax(dim=1)
                correct += (preds == labels).sum().item()

        epoch_loss = running_loss / len(train_dataset)
        val_epoch_loss = val_loss / len(val_dataset)
        val_acc = correct / len(val_dataset)

        print(f"--> Epoch {epoch+1} Complete | Train Loss: {epoch_loss:.4f} | Val Loss: {val_epoch_loss:.4f} | Val Acc: {val_acc:.4f}")

        if val_epoch_loss < best_val_loss:
            best_val_loss = val_epoch_loss
            torch.save(model.state_dict(), 'best_skin_model.pth')
            print("--> Best checkpoint updated: best_skin_model.pth")

if __name__ == '__main__':
    main()