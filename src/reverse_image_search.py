import torch
import numpy
import torch.nn as nn
import torchvision.models as models
from torchvision import datasets, transforms
from torch import reshape
from tqdm import tqdm
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors


def check_working():
    if torch.cuda.is_available():
        return f'Device: {torch.cuda.get_device_name()} ' \
               f'\n {torch.cuda.get_device_properties(torch.cuda.current_device())} ' \
               f'\n {torch.cuda.get_device_capability()}'
    else:
        return f'Not working'


def load_and_preprocess(img_folder):
    """ Since ResNet is trained on 224x224 RGB images, we need to resize the images to accomodate for that"""
    target_size = (224, 224, 3)

    # This is not ideal because of the whitespace around each patent drawing
    preprocess = transforms.Compose([
        transforms.Resize((target_size[0], target_size[1])),
        transforms.ToTensor()
    ])

    dataset = datasets.ImageFolder(img_folder, transform=preprocess)
    return dataset


def create_feature_extractor():
    """ Generates a feature extractor from a pre-trained ResNet50 model and applies it to images"""
    # Get a pre-trained ResNet-50 model
    resnet50 = models.resnet50(pretrained=True)

    # Freeze the network layers
    for param in resnet50.parameters():
        param.requires_grad = False

    # Remove the last layer of the NN to get a feature extractor
    feature_extractor = nn.Sequential(*list(resnet50.children())[:-1])

    return feature_extractor


def extract_features(img_folder):
    # Change device to GPU
    device = torch.device('cuda:0' if torch.cuda.is_available() else "cpu")

    # Create feature extractor from ResNet50
    extractor = create_feature_extractor()

    # Move F.E. to GPU
    extractor.to(device)

    # Preprocess all data
    data = load_and_preprocess(img_folder)

    # Extract features
    features = []

    for img in tqdm(data):
        # Need to figure out why there are instances with 2
        img = reshape(img[0], (1, 3, 224, 224)).to(device)

        with torch.no_grad():
            feature = extractor(img)
        features.append(feature.flatten().cpu().detach().numpy())

    return numpy.array(features)


def get_cluster_model(feature_list, n=5, pca=False):
    if pca:
        pca = PCA(n_components=n)
        pca.fit(feature_list)

        # This is the compressed feature list
        feature_list = pca.transform(feature_list)

    # Nearest neighbours algorithm
    neighbours = NearestNeighbors(n_neighbors=5, algorithm='ball_tree', metric='euclidean')
    neighbours.fit(feature_list)
    return neighbours


def predict(dirname='src/static'):
    # Extract features from all patent images
    patent_features = extract_features(dirname)

    # Designate query, reshape to keep correct # of features
    query = patent_features[-1].reshape(1, patent_features.shape[1])

    # Train model with training data (exclude query)
    model = get_cluster_model(patent_features[:-1])

    distances, indices = model.kneighbors(query)
    return distances, indices


