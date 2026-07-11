import torch

  # Path to your .pth file
file_path = '7_512_data_0.8.pth'

# Load the contents
model_data = torch.load(file_path)

# Print the contents
print(model_data)