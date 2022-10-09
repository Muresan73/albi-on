import torch
import torch.utils.data as Data
from utils.mongo_utils import db_distance_info_sanitized
from tqdm import tqdm
import torch.nn as nn
import haversine as hs
from torch.utils.tensorboard import SummaryWriter
writer = SummaryWriter()

n_inputs = 5
n_hidden = 10

# PyTorch models inherit from torch.nn.Module
class DistanceModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.hidden = torch.nn.Linear(n_inputs, n_hidden)
        self.mean_linear = torch.nn.Linear(n_hidden, 1)
        self.scale_linear = torch.nn.Linear(n_hidden, 1)

    def forward(self, x):
        outputs = self.hidden(x)
        # outputs = torch.relu(outputs)
        outputs = torch.sigmoid(outputs)

        mean = self.mean_linear(outputs)
        scale = torch.nn.functional.softplus(self.scale_linear(outputs))

        return torch.distributions.Normal(mean, scale)

class TinyModel(torch.nn.Module):

    def __init__(self):
        super(TinyModel, self).__init__()

        self.linear1 = torch.nn.Linear(5, 1)
        self.activation = torch.nn.ReLU()

    def forward(self, x):
        x = self.linear1(x)
        x = self.activation(x)
        return x

# model = DistanceModel()
# model = torch.nn.Sequential(
#     torch.nn.Linear(5, 1),
#     torch.nn.Flatten(0, 1)
# )
model = TinyModel()

# Optimizers specified in the torch.optim package
optimizer = torch.optim.SGD(model.parameters(), lr=1e-3, weight_decay=0.1)
loss_fn = torch.nn.MSELoss()
BATCH = 64

df = db_distance_info_sanitized()
X = df.loc[:, ~df.columns.isin(['_id', 'distance_time'])]
Y = df['distance_time']
# generate distance from target
X['distance_km'] = list(map(hs.haversine, zip(X["origin.lat"], X["origin.lon"]), zip(X["target.lat"], X["target.lon"])))

tensor_x = torch.Tensor(X.values) # transform to torch tensor
tensor_y = torch.Tensor(Y.values)

dataset = Data.TensorDataset(tensor_x,tensor_y)
training_loader = Data.DataLoader(dataset, batch_size = BATCH, shuffle = True)

# def loss_fn(y_hat, y):
#     negloglik = -y_hat.log_prob(y)
#     return torch.mean(negloglik)

for epoch in tqdm(range(100)):

    # Here, we use enumerate(training_loader) instead of
    # iter(training_loader) so that we can track the batch
    # index and do some intra-epoch reporting
    for i, data in enumerate(training_loader):
        # Every data instance is an input + label pair
        inputs, labels = data

        # Zero your gradients for every batch!
        optimizer.zero_grad()

        # Make predictions for this batch
        outputs = model(inputs)

        # Compute the loss and its gradients
        loss = loss_fn(outputs, labels)
        writer.add_scalar("Loss/train", loss, epoch)
        loss.backward()

        # Adjust learning weights
        optimizer.step()

writer.flush()
writer.close()

import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF

kernel = 1 * RBF(length_scale=1.0, length_scale_bounds=(1e-2, 1e2))
gaussian_process = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=9)
gaussian_process.fit(X_train, y_train)

lon = np.linspace(17.8,18.2,20)
lat = np.linspace(59.4,59.2,20)
space = [[a,b,hs.haversine((a,b),(18.0591,59.330767))] for a in lon for b in lat]
from scraper import plot

import pandas as pd
tlon = np.full(400,18.0591)
tlat = np.full(400,59.330767)

data = torch.Tensor(space)
pred = torch.flatten(model(data)).detach().numpy()

df = pd.DataFrame({'origin.lon':[item[0] for item in space],'origin.lat':[item[1] for item in space],'distance_time':pred})

plot.distance_region(df.values)