# Créer un README dans backend/models/
@"
# Models Directory

⚠️ **Les fichiers modèles (.pth) sont trop volumineux pour Git (>100 MB).**

## 📥 Téléchargement du Modèle

Téléchargez le modèle pré-entraîné depuis les **GitHub Releases** :

👉 [**Télécharger best_model.pth (161 MB)**](https://github.com/VOTRE_USERNAME/UnblurAI/releases/latest)

## 📂 Installation

1. Téléchargez ``best_model.pth`` depuis les releases
2. Placez-le dans ce dossier : ``backend/models/best_model.pth``
3. Lancez l'application :

````bash
docker compose up --build
````

## Détails du Modèle
Architecture : U-Net Enhanced (4-channel input)
Paramètres : 63.6M
Performance : +0.87 dB PSNR moyen (Q5-Q30)
Entraînement : 55 epochs sur DIV2K (1h30 sur T4)
Taille : 161 MB

## 🔧 Entraîner Votre Propre Modèle
Consultez le notebook de training disponible dans les releases ou dans docs/training.md.
"@ | Out-File -FilePath backend/models/README.md -Encoding UTF8

