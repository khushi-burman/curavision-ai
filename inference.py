import torch
import torchvision.transforms as transforms
from PIL import Image
import timm

# Class mapping for HAM10000 dataset
CLASS_NAMES = {
    0: 'Actinic keratoses (akiec)',
    1: 'Basal cell carcinoma (bcc)',
    2: 'Benign keratosis-like lesions (bkl)',
    3: 'Dermatofibroma (df)',
    4: 'Melanoma (mel)',
    5: 'Melanocytic nevi (nv)',
    6: 'Vascular lesions (vasc)'
}

# Inference preprocessing pipeline
infer_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def load_skin_model(model_path='best_skin_model.pth'):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = timm.create_model('efficientnet_b4', pretrained=False, num_classes=7)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model = model.to(device)
    model.eval()
    return model, device

def predict_image(image_path_or_pil, model, device):
    if isinstance(image_path_or_pil, str):
        image = Image.open(image_path_or_pil).convert('RGB')
    else:
        image = image_path_or_pil.convert('RGB')

    tensor = infer_transforms(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(tensor)
        probs = torch.softmax(outputs, dim=1)[0]
        pred_class = torch.argmax(probs).item()

    return {
        'class_id': pred_class,
        'label': CLASS_NAMES[pred_class],
        'confidence': float(probs[pred_class].cpu().numpy()),
        'all_probabilities': {CLASS_NAMES[i]: float(probs[i].cpu().numpy()) for i in range(7)}
    }

if __name__ == '__main__':
    # Test inference on a sample test image
    model, device = load_skin_model()
    # Replace with an actual relative image path to test
    print("Inference engine initialized successfully!")