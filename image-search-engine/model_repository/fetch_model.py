import torch
from torchvision.models import EfficientNet_B3_Weights, efficientnet_b3

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Instantiate the model
model = efficientnet_b3(weights=EfficientNet_B3_Weights.IMAGENET1K_V1)

# Set the model to evaluation mode
model.eval()

# Use a GPU (if available) for inference
model = model.to(device)

# Save the entire model to a file
traced_model = torch.jit.trace(model, torch.randn(1, 3, 300, 300).to(device))
torch.jit.save(traced_model, "./efficientnet_b3/1/model.pt")
