# Training Notebooks

Ce dossier contient les notebooks Jupyter pour l'entraînement et l'évaluation du modèle UnblurAI.

## Notebooks Disponibles

### training_notebook.ipynb

Notebook complet pour l'entraînement du modèle U-Net Enhanced sur le dataset DIV2K.

**Contenu :**
- Chargement et préparation du dataset DIV2K
- Architecture du modèle U-Net Enhanced (4-channel input)
- Configuration des optimisations (Residual Learning, Quality-Aware Conditioning)
- Loss multi-composantes (Charbonnier + MS-SSIM + Edge)
- Entraînement avec augmentation de données
- Évaluation sur plusieurs niveaux de qualité JPEG (Q5, Q10, Q20, Q30)
- Sauvegarde du meilleur modèle

**Utilisation :**

Ce notebook est conçu pour être exécuté sur Google Colab avec GPU.

1. Ouvrez le notebook dans Google Colab
2. Activez le GPU (Runtime > Change runtime type > GPU)
3. Téléchargez le dataset DIV2K
4. Exécutez toutes les cellules
5. Le modèle entraîné sera sauvegardé dans `best_model.pth`

**Résultats Attendus :**

Après 55 epochs (~1h30 sur T4 GPU) :
- PSNR Q5: +1.01 dB
- PSNR Q10: +1.00 dB
- PSNR Q20: +0.80 dB
- PSNR Q30: +0.67 dB
- Moyenne: +0.87 dB PSNR

## Dataset

Le notebook utilise le dataset **DIV2K** :
- 800 images d'entraînement haute résolution
- 50 images de validation
- Téléchargement : [DIV2K Dataset](https://data.vision.ee.ethz.ch/cvl/DIV2K/)

## Configuration Recommandée

- **GPU** : NVIDIA T4 ou supérieur
- **RAM** : 12 GB minimum
- **Stockage** : 5 GB (dataset + modèle + checkpoints)
- **Durée** : 1h30 pour 55 epochs

## Modifications Possibles

Pour améliorer les performances (+0.3-0.6 dB PSNR) :

1. **Perceptual Loss** : Ajouter VGG relu3_3 loss
2. **Patch Size** : Augmenter à 384x384
3. **Epochs** : Augmenter à 120 epochs
4. **Ensemble** : Entraîner 3 modèles avec seeds différentes
5. **Attention** : Ajouter CBAM/SE attention blocks

Voir le README principal pour plus de détails sur ces optimisations.

## Troubleshooting

### CUDA Out of Memory

Réduisez le batch size :
```python
BATCH_SIZE = 4  # au lieu de 8
```

### Dataset non trouvé

Vérifiez le chemin du dataset :
```python
TRAIN_DIR = "DIV2K/DIV2K_train_HR"
VAL_DIR = "DIV2K/DIV2K_valid_HR"
```

### Loss qui n'améliore pas

Vérifiez la normalisation des images (doit être [-1, 1]).
