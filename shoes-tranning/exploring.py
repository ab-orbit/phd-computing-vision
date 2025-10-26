import kagglehub
#https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-dataset

# Download latest version
path = kagglehub.dataset_download("paramaggarwal/fashion-product-images-dataset")

print("Path to dataset files:", path)