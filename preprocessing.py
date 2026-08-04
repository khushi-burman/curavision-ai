import pandas as pd
from PIL import Image
import numpy as np

# Load metadata
df = pd.read_csv("HAM10000_metadata.csv")

print("First 5 rows:")
print(df.head())

print("\nDataset Information:")
print(df.info())

print("\nMissing Values:")
print(df.isnull().sum())

print("\nDisease Distribution:")
print(df["dx"].value_counts())

from sklearn.model_selection import train_test_split

# 1. Map lesion image ID to file path
# 2. Stratified Split (e.g., 80% Train, 10% Val, 10% Test)
train_df, test_df = train_test_split(df, test_size=0.2, stratify=df['dx'], random_state=42)
val_df, test_df = train_test_split(test_df, test_size=0.5, stratify=test_df['dx'], random_state=42)

import os
from glob import glob

# Create image path dictionary
files = glob("HAM10000_images_part_*/*.jpg")
print(len(files))
print(files[:5])
image_path = {
    os.path.splitext(os.path.basename(x))[0]: x
    for x in files
}
# Add image path to dataframe
df["path"] = df["image_id"].map(image_path.get)

print(df[["image_id", "path"]].head())

# Save the updated metadata
df.to_csv("HAM10000_preprocessed.csv", index=False)

print("Preprocessing completed successfully!")
print(df.isnull().sum())
# Fill missing age values with median
df["age"] = df["age"].fillna(df["age"].median())

print("\nMissing values after filling:")
print(df.isnull().sum())
from sklearn.preprocessing import LabelEncoder

# Create Label Encoder
le = LabelEncoder()

# Convert disease names into numbers
df["label"] = le.fit_transform(df["dx"])

print("\nDisease Label Mapping:")
for disease, label in zip(le.classes_, range(len(le.classes_))):
    print(f"{disease} --> {label}")

print("\nFirst 5 rows:")
print(df[["dx", "label"]].head())

# Load one sample image
sample_path = df["path"].iloc[0]

img = Image.open(sample_path)

print("Original Image Size:", img.size)

# Resize image
img = img.resize((28, 28))

print("Resized Image Size:", img.size)

# Convert image to NumPy array
img_array = np.array(img)

print("Image Array Shape:", img_array.shape)
# Load all images into NumPy arrays

X = []
y = []

for index, row in df.iterrows():

    img = Image.open(row["path"])
    img = img.resize((28, 28))
    img = np.array(img)

    X.append(img)
    y.append(row["label"])

# Convert lists to NumPy arrays
X = np.array(X)
y = np.array(y)

print("\nDataset Loaded Successfully!")

print("X Shape:", X.shape)
print("y Shape:", y.shape)
# Normalize image pixels

X = X.astype("float32") / 255.0

print("\nImages Normalized Successfully!")

print("Minimum Pixel Value:", X.min())
print("Maximum Pixel Value:", X.max())
# Normalize image pixels

np.save("processed_data/X.npy", X)
np.save("processed_data/y.npy", y)

print("\nProcessed dataset saved successfully!")

# Verify saved files
X_loaded = np.load("processed_data/X.npy")
y_loaded = np.load("processed_data/y.npy")

print("\nVerification Successful!")
print("Loaded X Shape:", X_loaded.shape)
print("Loaded y Shape:", y_loaded.shape)

from sklearn.model_selection import train_test_split

# 80% Train, 20% Temporary
train_df, temp_df = train_test_split(
    df,
    test_size=0.2,
    stratify=df["label"],
    random_state=42
)

# Split the remaining 20% into 10% Validation and 10% Test
val_df, test_df = train_test_split(
    temp_df,
    test_size=0.5,
    stratify=temp_df["label"],
    random_state=42
)
train_df.to_csv("processed_data/train.csv", index=False)
val_df.to_csv("processed_data/val.csv", index=False)
test_df.to_csv("processed_data/test.csv", index=False)

print("\nTrain, Validation and Test datasets saved successfully!")
print("\nDataset Sizes:")
print("Training :", len(train_df))
print("Validation:", len(val_df))
print("Testing   :", len(test_df))