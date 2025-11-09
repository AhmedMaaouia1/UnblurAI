# Models Directory

**Les fichiers modèles (.pth) sont trop volumineux pour Git (>100 MB).**

## Téléchargement du Modèle

Téléchargez le modèle pré-entraîné depuis les **GitHub Releases** :

[**Télécharger best_model.pth (161 MB)**](https://github.com/AhmedMaaouia1/UnblurAI/releases/latest)

## Installation

### Option 1 : Téléchargement Automatique (Linux/Mac)

```bash
curl -L -o backend/models/best_model.pth \
  https://github.com/AhmedMaaouia1/UnblurAI/releases/download/v1.0.0/best_model.pth
```

### Option 2 : Téléchargement Automatique (Windows PowerShell)

```powershell
Invoke-WebRequest -Uri "https://github.com/AhmedMaaouia1/UnblurAI/releases/download/v1.0.0/best_model.pth" `
  -OutFile "backend/models/best_model.pth"
```

### Option 3 : Téléchargement Manuel

1. Allez sur [Releases](https://github.com/AhmedMaaouia1/UnblurAI/releases/latest)
2. Téléchargez `best_model.pth` (161 MB)
3. Placez-le dans ce dossier : `backend/models/best_model.pth`

## Vérification

Après téléchargement, lancez l'application :

```bash
docker compose up --build
```

L'API devrait démarrer sur `http://localhost:8000` et afficher :

```
INFO:     Model loaded successfully from models/best_model.pth
INFO:     Application startup complete.
```

## Détails du Modèle

- **Architecture** : U-Net Enhanced (4-channel input)
- **Paramètres** : 63,585,731 (63.6M)
- **Input** : 4 canaux (RGB + Q/100 conditioning)
- **Output** : Delta résiduel (3 canaux RGB)
- **Performance** : +0.87 dB PSNR moyen (Q5-Q30)
- **Entraînement** : 55 epochs sur DIV2K (1h30 sur T4 GPU)
- **Taille** : 161 MB

## Entraîner Votre Propre Modèle

Si vous souhaitez entraîner votre propre modèle :

1. Consultez le notebook de training disponible dans les [Releases](https://github.com/AhmedMaaouia1/UnblurAI/releases)
2. Téléchargez le dataset [DIV2K](https://data.vision.ee.ethz.ch/cvl/DIV2K/)
3. Suivez les instructions dans le notebook

Le modèle entraîné sera automatiquement sauvegardé dans ce dossier.

## Important

**Ne commitez jamais les fichiers .pth dans Git.**

Ils sont automatiquement exclus via `.gitignore` car trop volumineux (>100 MB).
Pour partager un nouveau modèle, utilisez GitHub Releases.
