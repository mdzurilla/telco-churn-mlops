import torch
import torch.nn as nn

class ChurnNN(nn.Module):
    def __init__(self, input_dim, hidden_dim, dropout_rate=0.0):
        super().__init__()
        
        self.model = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return self.model(x)