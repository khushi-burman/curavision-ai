import importlib.util

# List of required packages mapped to their import names
packages_to_check = {
    "FastAPI": "fastapi",
    "Uvicorn": "uvicorn",
    "Pydantic": "pydantic",
    "Streamlit": "streamlit",
    "Requests": "requests",
    "PyTorch (torch)": "torch",
    "Torchvision": "torchvision",
    "TIMM": "timm",
    "PyTorch Grad-CAM": "pytorch_grad_cam",
    "Joblib": "joblib",
    "Pandas": "pandas",
    "Pillow (PIL)": "PIL",
    "LangChain Community": "langchain_community",
    "ChromaDB": "chromadb",
    "Ollama": "ollama"
}

print("=== CuraVision AI Environment Check ===\n")
missing_packages = []

for display_name, import_name in packages_to_check.items():
    spec = importlib.util.find_spec(import_name)
    if spec is not None:
        print(f"✅ {display_name:<20} -> Installed")
    else:
        print(f"❌ {display_name:<20} -> MISSING")
        missing_packages.append(import_name)

print("\n----------------------------------------")
if missing_packages:
    print(f"Status: {len(missing_packages)} package(s) missing.")
    # Map back standard names for easy pip install if needed
    install_map = {
        "pytorch_grad_cam": "pytorch-grad-cam",
        "PIL": "pillow",
        "langchain_community": "langchain-community"
    }
    pip_names = [install_map.get(pkg, pkg) for pkg in missing_packages]
    print(f"\nTo install missing packages, run:\npip install {' '.join(pip_names)}")
else:
    print("Status: All required libraries are installed and ready to go! 🎉")