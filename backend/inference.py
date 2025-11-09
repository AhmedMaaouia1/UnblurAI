"""
Fonctions de prétraitement, inférence et post-traitement pour la restauration d'images.
Ces fonctions reproduisent exactement le pipeline utilisé lors de l'entraînement.
"""

import torch
import numpy as np
from PIL import Image
from typing import Tuple
import torch.nn.functional as F


def correct_image_orientation(image: Image.Image) -> Image.Image:
    """
    Corrige l'orientation de l'image en fonction des métadonnées EXIF.
    """
    try:
        from PIL import ImageOps
        return ImageOps.exif_transpose(image)
    except Exception:
        return image


def preprocess_image(image: Image.Image, quality: int = 5) -> Tuple[torch.Tensor, Tuple[int, int]]:
    """
    Prétraite l'image pour l'inférence avec le modèle optimisé.
    
    🆕 MODÈLE OPTIMISÉ:
    - Ajoute un canal Q/100 (quality-aware conditioning)
    - Input final: 4 canaux (RGB + Q)
    
    Étapes :
    1. Convertir en RGB
    2. Corriger l'orientation EXIF
    3. Convertir en tenseur float32 [0, 1]
    4. Normaliser en [-1, 1]
    5. 🆕 Ajouter le canal Q/100
    
    Args:
        image: Image PIL
        quality: Qualité JPEG estimée (5-30) pour le conditioning
    
    Returns:
        Tuple contenant :
        - Tenseur normalisé de forme (1, 4, H, W)  🆕 4 canaux
        - Dimensions originales (H, W)
    """
    # Convertir en RGB si nécessaire
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Corriger l'orientation
    image = correct_image_orientation(image)
    
    # Sauvegarder les dimensions originales
    original_size = (image.height, image.width)
    
    # Convertir en tenseur numpy puis PyTorch
    img_array = np.array(image, dtype=np.float32) / 255.0  # [0, 1]
    img_tensor = torch.from_numpy(img_array).permute(2, 0, 1)  # (3, H, W)
    
    # Normaliser en [-1, 1] : (x - 0.5) / 0.5
    img_tensor = (img_tensor - 0.5) / 0.5
    
    # Ajouter la dimension batch
    img_tensor = img_tensor.unsqueeze(0)  # (1, 3, H, W)
    
    # 🆕 Créer le canal de qualité normalisé [0, 1]
    _, _, h, w = img_tensor.shape
    quality_channel = torch.full(
        (1, 1, h, w),
        quality / 100.0,
        dtype=torch.float32
    )
    
    # 🆕 Concaténer RGB + Q
    img_tensor = torch.cat([img_tensor, quality_channel], dim=1)  # (1, 4, H, W)
    
    return img_tensor, original_size


def pad_to_multiple_of_16(tensor: torch.Tensor) -> Tuple[torch.Tensor, Tuple[int, int, int, int]]:
    """
    Ajoute du padding pour que H et W soient multiples de 16.
    Utilise le mode 'reflect' pour éviter les artefacts de bord.
    
    🆕 Compatible avec 4 canaux (RGB + Q)
    
    Args:
        tensor: Tenseur de forme (1, 4, H, W)  🆕 4 canaux
    
    Returns:
        Tuple contenant :
        - Tenseur paddé
        - Padding appliqué (left, right, top, bottom)
    """
    _, _, h, w = tensor.shape
    
    # Calculer le padding nécessaire
    pad_h = (16 - h % 16) % 16
    pad_w = (16 - w % 16) % 16
    
    # Répartir le padding de manière équilibrée
    pad_top = pad_h // 2
    pad_bottom = pad_h - pad_top
    pad_left = pad_w // 2
    pad_right = pad_w - pad_left
    
    # Appliquer le padding en mode reflect
    if pad_h > 0 or pad_w > 0:
        tensor = F.pad(tensor, (pad_left, pad_right, pad_top, pad_bottom), mode='reflect')
    
    return tensor, (pad_left, pad_right, pad_top, pad_bottom)


def remove_padding(tensor: torch.Tensor, padding: Tuple[int, int, int, int]) -> torch.Tensor:
    """
    Retire le padding ajouté précédemment.
    
    Args:
        tensor: Tenseur paddé de forme (1, 3, H, W)
        padding: (left, right, top, bottom)
    
    Returns:
        Tenseur sans padding
    """
    pad_left, pad_right, pad_top, pad_bottom = padding
    
    if pad_left == 0 and pad_right == 0 and pad_top == 0 and pad_bottom == 0:
        return tensor
    
    _, _, h, w = tensor.shape
    
    # Calculer les indices de découpe
    left = pad_left
    right = w - pad_right if pad_right > 0 else w
    top = pad_top
    bottom = h - pad_bottom if pad_bottom > 0 else h
    
    return tensor[:, :, top:bottom, left:right]


def postprocess_image(tensor: torch.Tensor) -> Image.Image:
    """
    Convertit le tenseur de sortie du modèle en image PIL.
    
    Étapes :
    1. Dénormaliser de [-1, 1] vers [0, 1]
    2. Clamp pour garantir [0, 1]
    3. Convertir en numpy puis PIL
    
    Args:
        tensor: Tenseur de forme (1, 3, H, W) dans [-1, 1]
    
    Returns:
        Image PIL
    """
    # Retirer la dimension batch
    tensor = tensor.squeeze(0)  # (3, H, W)
    
    # Dénormaliser : x * 0.5 + 0.5
    tensor = tensor * 0.5 + 0.5
    
    # Clamp pour garantir [0, 1]
    tensor = torch.clamp(tensor, 0, 1)
    
    # Convertir en numpy (H, W, 3)
    img_array = tensor.permute(1, 2, 0).cpu().numpy()
    img_array = (img_array * 255).astype(np.uint8)
    
    # Convertir en PIL
    image = Image.fromarray(img_array, mode='RGB')
    
    return image


def infer_single(model: torch.nn.Module, image: Image.Image, device: torch.device, quality: int = 5) -> Image.Image:
    """
    Effectue l'inférence complète sur une seule image avec résidual learning.
    
    🆕 MODÈLE OPTIMISÉ:
    - Input: 4 canaux (RGB + Q/100)
    - Output: Delta résiduel
    - Reconstruction: restored = input_rgb + delta
    
    Args:
        model: Modèle U-Net
        image: Image PIL à restaurer
        device: Device PyTorch
        quality: Qualité JPEG estimée (5-30)
    
    Returns:
        Image restaurée
    """
    # Prétraitement (avec canal Q)
    img_tensor, original_size = preprocess_image(image, quality)
    img_tensor = img_tensor.to(device)
    
    # Padding
    img_padded, padding = pad_to_multiple_of_16(img_tensor)
    
    # Inférence
    with torch.no_grad():
        if device.type == 'cuda':
            with torch.amp.autocast('cuda'):
                # 🆕 Le modèle retourne un delta
                delta = model(img_padded)
        else:
            delta = model(img_padded)
    
    # 🆕 Reconstruction résiduelle
    # Extraire les 3 premiers canaux RGB de l'input
    input_rgb = img_padded[:, :3, :, :]
    
    # Ajouter le delta
    restored = input_rgb + delta
    
    # Clamp dans [-1, 1]
    restored = torch.clamp(restored, -1, 1)
    
    # Retirer le padding
    restored = remove_padding(restored, padding)
    
    # Post-traitement
    restored_image = postprocess_image(restored)
    
    return restored_image


def infer_tiled(model: torch.nn.Module, image: Image.Image, device: torch.device,
                tile_size: int = 512, overlap: int = 32, quality: int = 10) -> Image.Image:
    """
    Effectue l'inférence par tuiles pour les images très grandes avec résidual learning.
    Permet d'éviter les erreurs de mémoire (OOM).
    
    🆕 MODÈLE OPTIMISÉ:
    - Input: 4 canaux (RGB + Q/100)
    - Output: Delta résiduel
    - Reconstruction: restored = input_rgb + delta
    
    Args:
        model: Modèle U-Net
        image: Image PIL à restaurer
        device: Device PyTorch
        tile_size: Taille des tuiles (doit être multiple de 16)
        overlap: Chevauchement entre tuiles pour éviter les artefacts
        quality: Qualité JPEG estimée (5-30)
    
    Returns:
        Image restaurée
    """
    # Prétraitement (avec canal Q)
    img_tensor, original_size = preprocess_image(image, quality)
    img_tensor = img_tensor.to(device)
    
    _, _, h, w = img_tensor.shape
    
    # Créer le tenseur de sortie (3 canaux RGB pour l'output)
    output_tensor = torch.zeros((1, 3, h, w), device=device, dtype=img_tensor.dtype)
    weight_tensor = torch.zeros((1, 3, h, w), device=device, dtype=img_tensor.dtype)
    
    # Calculer le stride
    stride = tile_size - overlap * 2
    
    # Parcourir l'image par tuiles
    for y in range(0, h, stride):
        for x in range(0, w, stride):
            # Extraire la tuile avec overlap
            y_start = max(0, y - overlap)
            x_start = max(0, x - overlap)
            y_end = min(h, y + tile_size + overlap)
            x_end = min(w, x + tile_size + overlap)
            
            tile = img_tensor[:, :, y_start:y_end, x_start:x_end]
            
            # Padding de la tuile
            tile_padded, padding = pad_to_multiple_of_16(tile)
            
            # Inférence
            with torch.no_grad():
                if device.type == 'cuda':
                    with torch.amp.autocast('cuda'):
                        # 🆕 Le modèle retourne un delta
                        delta = model(tile_padded)
                else:
                    delta = model(tile_padded)
            
            # 🆕 Reconstruction résiduelle
            tile_rgb = tile_padded[:, :3, :, :]
            tile_restored = tile_rgb + delta
            tile_restored = torch.clamp(tile_restored, -1, 1)
            
            # Retirer le padding
            tile_restored = remove_padding(tile_restored, padding)
            
            # Calculer les poids (gaussian pour smooth blending)
            tile_h, tile_w = tile_restored.shape[2:]
            weight = torch.ones_like(tile_restored)
            
            # Ajouter au tenseur de sortie
            output_tensor[:, :, y_start:y_end, x_start:x_end] += tile_restored
            weight_tensor[:, :, y_start:y_end, x_start:x_end] += weight
    
    # Normaliser par les poids
    output_tensor = output_tensor / weight_tensor
    
    # Post-traitement
    restored_image = postprocess_image(output_tensor)
    
    return restored_image


def restore_image(model: torch.nn.Module, image: Image.Image, device: torch.device,
                  use_tiling: bool = None, max_size: int = 3000, quality: int = 5) -> Image.Image:
    """
    Fonction principale de restauration d'image avec modèle optimisé.
    Choisit automatiquement entre inférence normale ou par tuiles.
    
    🆕 MODÈLE OPTIMISÉ:
    - Paramètre quality pour le conditioning (Q/100)
    - Résidual learning (delta + input)
    
    Args:
        model: Modèle U-Net
        image: Image PIL à restaurer
        device: Device PyTorch
        use_tiling: Forcer l'utilisation de tuiles (None = auto)
        max_size: Taille maximale avant d'utiliser les tuiles
        quality: Qualité JPEG estimée (5-30) pour le conditioning
    
    Returns:
        Image restaurée
    """
    # Décider si on utilise les tuiles
    if use_tiling is None:
        use_tiling = max(image.width, image.height) > max_size
    
    if use_tiling:
        print(f"Image large ({image.width}x{image.height}), utilisation de l'inférence par tuiles")
        return infer_tiled(model, image, device, quality=quality)
    else:
        return infer_single(model, image, device, quality=quality)
