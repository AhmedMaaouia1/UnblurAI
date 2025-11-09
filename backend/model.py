"""
Définition du modèle U-Net pour la restauration d'images.
Cette architecture est identique à celle utilisée lors de l'entraînement sur Google Colab.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class ResidualBlock(nn.Module):
    """Bloc résiduel avec convolutions 3x3"""
    
    def __init__(self, channels):
        super(ResidualBlock, self).__init__()
        self.conv1 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(channels)
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(channels)
        self.relu = nn.ReLU(inplace=True)
    
    def forward(self, x):
        residual = x
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += residual  # Skip connection
        out = self.relu(out)
        return out
        return out


class UNet(nn.Module):
    """
    U-Net Enhanced pour la restauration d'images avec Résidual Learning.
    Architecture identique au code d'entraînement avec alignement par padding.
    
    🆕 OPTIMISATIONS APPLIQUÉES:
    - Entrée : 4 canaux (RGB + Q/100) au lieu de 3
    - Sortie : Delta résiduel (correction à appliquer)
    - Reconstruction: restored = input_rgb + delta
    
    Entrée : Image normalisée [-1, 1], 4 canaux (RGB + Q/100)
    Sortie : Delta résiduel [-1, 1], 3 canaux (RGB)
    """
    
    def __init__(self, in_channels=4, out_channels=3):
        super(UNet, self).__init__()
        self.n_channels = in_channels
        self.n_classes = out_channels

        # Encodeurs (downsampling)
        self.enc1 = self._encoder_block(in_channels, 64)
        self.enc2 = self._encoder_block(64, 128)
        self.enc3 = self._encoder_block(128, 256)
        self.enc4 = self._encoder_block(256, 512)

        # Bottleneck avec convolutions dilatées
        self.bottleneck = nn.Sequential(
            nn.Conv2d(512, 1024, 3, padding=2, dilation=2),
            nn.BatchNorm2d(1024),
            nn.ReLU(inplace=True),
            ResidualBlock(1024),
            ResidualBlock(1024),
            nn.Dropout2d(0.5)
        )

        # Décodeurs (upsampling)
        self.dec4 = self._decoder_block(1024, 512)
        self.dec3 = self._decoder_block(512, 256)
        self.dec2 = self._decoder_block(256, 128)
        self.dec1 = self._decoder_block(128, 64)

        # Couches de réduction pour les skip connections
        self.reduce4 = nn.Conv2d(1024, 512, 1)
        self.reduce3 = nn.Conv2d(512, 256, 1)
        self.reduce2 = nn.Conv2d(256, 128, 1)
        self.reduce1 = nn.Conv2d(128, 64, 1)

        # 🆕 Couche de sortie RÉSIDUELLE (Tanh pour delta [-1, 1])
        self.final = nn.Sequential(
            nn.Conv2d(64, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, out_channels, 1),
            nn.Tanh()  # Delta dans [-1, 1]
        )

        self.pool = nn.MaxPool2d(2)
        self.upsample = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)

    def _encoder_block(self, in_ch, out_ch):
        """Bloc d'encodeur avec convolution, BatchNorm, ReLU, ResidualBlock et Dropout"""
        return nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            ResidualBlock(out_ch),
            nn.Dropout2d(0.1)
        )

    def _decoder_block(self, in_ch, out_ch):
        """Bloc de décodeur avec convolution, BatchNorm, ReLU, ResidualBlock et Dropout"""
        return nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            ResidualBlock(out_ch),
            nn.Dropout2d(0.1)
        )

    def _align_tensors(self, dec, enc):
        """
        Aligne les tenseurs décodeur et encodeur avec padding si nécessaire.
        Reproduit exactement la logique du code d'entraînement.
        
        Args:
            dec: tenseur du décodeur (après upsampling)
            enc: tenseur de l'encodeur (skip connection)
        
        Returns:
            dec: tenseur décodeur paddé pour matcher la taille de enc
        """
        if dec.size() != enc.size():
            diffY = enc.size(2) - dec.size(2)
            diffX = enc.size(3) - dec.size(3)

            # Padding: [left, right, top, bottom]
            dec = nn.functional.pad(dec, [diffX // 2, diffX - diffX // 2,
                                         diffY // 2, diffY - diffY // 2])

        return dec

    def forward(self, x):
        # 🆕 x contient 4 canaux: RGB + Q/100
        # Encodeur avec sauvegarde des features
        enc1 = self.enc1(x)                    # [B, 64, H, W]
        enc2 = self.enc2(self.pool(enc1))      # [B, 128, H/2, W/2]
        enc3 = self.enc3(self.pool(enc2))      # [B, 256, H/4, W/4]
        enc4 = self.enc4(self.pool(enc3))      # [B, 512, H/8, W/8]

        # Bottleneck
        bottleneck = self.bottleneck(self.pool(enc4))  # [B, 1024, H/16, W/16]

        # Décodeur avec skip connections et alignement automatique par padding
        dec4 = self.dec4(self.upsample(bottleneck))    # [B, 512, H/8, W/8]
        dec4 = self._align_tensors(dec4, enc4)         # Alignement par padding
        dec4 = self.reduce4(torch.cat([dec4, enc4], dim=1))

        dec3 = self.dec3(self.upsample(dec4))          # [B, 256, H/4, W/4]
        dec3 = self._align_tensors(dec3, enc3)
        dec3 = self.reduce3(torch.cat([dec3, enc3], dim=1))

        dec2 = self.dec2(self.upsample(dec3))          # [B, 128, H/2, W/2]
        dec2 = self._align_tensors(dec2, enc2)
        dec2 = self.reduce2(torch.cat([dec2, enc2], dim=1))

        dec1 = self.dec1(self.upsample(dec2))          # [B, 64, H, W]
        dec1 = self._align_tensors(dec1, enc1)
        dec1 = self.reduce1(torch.cat([dec1, enc1], dim=1))

        # 🆕 Sortie RÉSIDUELLE (delta à ajouter à l'input)
        delta = self.final(dec1)

        return delta


def load_model(model_path: str, device: torch.device) -> UNet:
    """
    Charge le modèle U-Net depuis un fichier de poids.
    Compatible avec les checkpoints créés sur Google Colab.
    
    🆕 MODÈLE OPTIMISÉ:
    - in_channels=4 (RGB + Q/100)
    - Sortie résiduelle (delta)
    
    Args:
        model_path: Chemin vers le fichier .pth
        device: Device PyTorch (cuda ou cpu)
    
    Returns:
        Modèle U-Net chargé en mode eval
    """
    model = UNet(in_channels=4, out_channels=3)  # 🆕 4 canaux d'entrée
    
    # Charger le checkpoint
    checkpoint = torch.load(model_path, map_location=device)
    
    # Vérifier si c'est un checkpoint complet ou juste un state_dict
    if isinstance(checkpoint, dict):
        if 'model_state_dict' in checkpoint:
            # Checkpoint complet avec optimizer, loss, etc.
            state_dict = checkpoint['model_state_dict']
        elif 'state_dict' in checkpoint:
            # Checkpoint avec clé 'state_dict'
            state_dict = checkpoint['state_dict']
        else:
            # Dictionnaire direct (state_dict)
            state_dict = checkpoint
    else:
        state_dict = checkpoint
    
    # Charger les poids
    model.load_state_dict(state_dict)
    
    # Mettre en mode évaluation
    model.to(device)
    model.eval()
    
    return model
