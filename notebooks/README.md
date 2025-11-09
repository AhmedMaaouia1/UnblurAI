# Training Notebooks

Ce dossier contient les notebooks Jupyter pour l'entraînement et l'évaluation du modèle UnblurAI.

## Notebooks Disponibles

### 2_Training_and_Evaluation_UNet_DIV2K_project.ipynb

Notebook complet pour l'entraînement du modèle U-Net Enhanced sur le dataset DIV2K.

**Contenu :**
- Chargement et préparation du dataset DIV2K
- Définition de la stratégie de **compression à la volée** (Q aléatoire [5, 30])
- Architecture du modèle `UNetEnhanced` (Entrée 4 canaux, `ResidualBlock`, sortie `Tanh()`)
- Configuration des optimisations (Residual Learning, Quality-Aware Conditioning)
- Loss multi-composantes (0.5 * Charbonnier + 0.3 * MS-SSIM + 0.2 * Edge)
- Boucle d'entraînement avec `ReduceLROnPlateau` et `GradScaler` (AMP)
- Évaluation quantitative et qualitative sur 50 images de validation
- Sauvegarde du meilleur modèle (`best_model.pth`) et des graphiques de résultats

**Utilisation :**

Ce notebook est conçu pour être exécuté sur Google Colab avec GPU.

1.  Ouvrez le notebook dans Google Colab.
2.  Activez le GPU (Exécution > Modifier le type d'exécution > T4 GPU).
3.  Assurez-vous que votre dataset DIV2K est dans le chemin `BASE_PATH` sur Google Drive.
4.  Exécutez toutes les cellules.
5.  Le modèle entraîné (`best_model.pth`) et les résultats (`loss_curve.png`, etc.) seront sauvegardés dans vos dossiers `models/` et `results/` sur Drive.

**Résultats Attendus :**

Après **60 époques (~1h 46m sur T4 GPU)** :
- PSNR Q5: **+1.12 dB**
- PSNR Q10: **+1.10 dB**
- PSNR Q20: **+0.91 dB**
- PSNR Q30: **+0.77 dB**
- Moyenne: **+0.98 dB PSNR**

## Dataset

Le notebook utilise le dataset **DIV2K** :
- 800 images d'entraînement haute résolution
- 100 images de validation (nous en utilisons 50 pour l'évaluation finale)
- Téléchargement : [DIV2K Dataset](https://data.vision.ee.ethz.ch/cvl/DIV2K/)

## Configuration Recommandée

- **GPU** : NVIDIA T4 ou supérieur
- **RAM** : 12 GB minimum
- **Stockage** : 5 GB (dataset + modèle + checkpoints)
- **Durée** : **~1h 46m** pour 60 époques

## Modifications Possibles

Pour améliorer les performances (mentionnées dans le README principal) :

1.  **Perceptual Loss** : Ajouter VGG relu3_3 loss
2.  **Patch Size** : Augmenter à 384x384
3.  **Epochs** : Augmenter à 120 epochs
4.  **Ensemble** : Entraîner 3 modèles avec seeds différentes
5.  **Attention** : Ajouter CBAM/SE attention blocks

Voir le README principal pour plus de détails sur ces optimisations.

## Troubleshooting

### CUDA Out of Memory

Réduisez le batch size dans la cellule [18] :
```python
BATCH_SIZE = 4  # au lieu de 8
```

### Dataset non trouvé
Vérifiez la variable BASE_PATH dans la cellule [8] pour qu'elle corresponde à votre arborescence Google Drive.

### Loss qui n'améliore pas (NaN)
Vérifiez la normalisation des images (doit être [-1, 1]) et que votre CombinedLoss (Cellule [13]) gère correctement les data_range (ex: ms_ssim(..., data_range=2.0, ...)).
