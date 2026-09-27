import torch
import torchvision.transforms as transforms
from PIL import Image
import timm
import numpy as np
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

CLASS_NAMES = {
    0: 'Actinic keratoses (akiec)',
    1: 'Basal cell carcinoma (bcc)',
    2: 'Benign keratosis-like lesions (bkl)',
    3: 'Dermatofibroma (df)',
    4: 'Melanoma (mel)',
    5: 'Melanocytic nevi (nv)',
    6: 'Vascular lesions (vasc)'
}

infer_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


def load_skin_model(model_path='skin_model/best_skin_model.pth'):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = timm.create_model('efficientnet_b4', pretrained=False, num_classes=7)
    
    # Load model weights onto appropriate device
    state_dict = torch.load(model_path, map_location=device, weights_only=True)
    model.load_state_dict(state_dict)
    model = model.to(device)
    model.eval()
    return model, device


def generate_gradcam(model, target_layer, input_tensor, rgb_img_normalized, target_category=None):
    # Ensure gradients are enabled for Grad-CAM backpropagation
    input_tensor = input_tensor.clone().detach().requires_grad_(True)
    
    # Initialize Grad-CAM on EfficientNet-B4's conv_head layer
    cam = GradCAM(model=model, target_layers=[target_layer])
    
    # Create target list
    targets = [ClassifierOutputTarget(target_category)] if target_category is not None else None
    
    # Pass input_tensor and targets positionally to remain compatible with all BaseCAM versions
    try:
        grayscale_cam = cam(input_tensor, targets)[0, :]
    except TypeError:
        grayscale_cam = cam(input_tensor=input_tensor, targets=targets)[0, :]
    
    # Overlay heatmap onto the RGB image
    visualization = show_cam_on_image(rgb_img_normalized, grayscale_cam, use_rgb=True)
    return Image.fromarray(visualization), grayscale_cam


def predict_image(image_path_or_pil, model, device, generate_heatmap=True):
    if isinstance(image_path_or_pil, str):
        image = Image.open(image_path_or_pil).convert('RGB')
    else:
        image = image_path_or_pil.convert('RGB')

    # Prepare 224x224 RGB array normalized to [0, 1] for Grad-CAM overlay
    resized_img = image.resize((224, 224))
    rgb_img_normalized = np.float32(resized_img) / 255.0

    tensor = infer_transforms(image).unsqueeze(0).to(device)

    # Perform inference forward pass
    with torch.no_grad():
        outputs = model(tensor)
        probs = torch.softmax(outputs, dim=1)[0]
        pred_class = torch.argmax(probs).item()

    result = {
        'class_id': pred_class,
        'label': CLASS_NAMES[pred_class],
        'confidence': float(probs[pred_class].cpu().numpy()),
        'all_probabilities': {CLASS_NAMES[i]: float(probs[i].cpu().numpy()) for i in range(7)}
    }

    if generate_heatmap:
        # EfficientNet-B4 final feature extractor layer in timm is model.conv_head
        target_layer = model.conv_head
        gradcam_img, _ = generate_gradcam(
            model, 
            target_layer, 
            tensor, 
            rgb_img_normalized, 
            target_category=pred_class
        )
        result['gradcam_overlay'] = gradcam_img

    return result


if __name__ == '__main__':
    model, device = load_skin_model()
    print("Inference engine with Grad-CAM initialized successfully!")