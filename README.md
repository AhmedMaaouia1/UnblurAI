# UnblurAI 🎨

> **AI-Powered JPEG Artifact Removal** - Restaurez la qualité de vos images compressées JPEG

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.1-red.svg)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://react.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

UnblurAI utilise un modèle U-Net Enhanced optimisé pour supprimer les artefacts de compression JPEG et restaurer les détails perdus de vos images.

## ✨ Caractéristiques

- 🎯 **Quality-Aware Conditioning** : Adaptation automatique au niveau de compression (Q5-Q30)
- 🔬 **Residual Learning** : Prédiction du delta optimal pour une restauration précise
- 🎨 **Loss Multi-Composantes** : Charbonnier + MS-SSIM + Edge Loss pour préserver les détails
- ⚡ **Compression JPEG Aléatoire** : Généralisation robuste sur toutes les qualités
- 🚀 **API REST** : Intégration facile dans vos workflows
- 🐳 **Docker Ready** : Déploiement en un clic

## 📊 Performances

Résultats sur le dataset DIV2K (50 images de validation):

| Qualité JPEG | PSNR Avant | PSNR Après | **Gain PSNR** | SSIM Avant | SSIM Après | **Gain SSIM** |
|-------------|-----------|-----------|--------------|-----------|-----------|--------------|
| **Q5**  | 24.47 dB | 25.48 dB | **+1.01 dB** ✅ | 0.6904 | 0.7378 | **+0.047** ✅ |
| **Q10** | 27.62 dB | 28.62 dB | **+1.00 dB** ✅ | 0.7922 | 0.8282 | **+0.036** ✅ |
| **Q20** | 30.26 dB | 31.06 dB | **+0.80 dB** ✅ | 0.8603 | 0.8820 | **+0.022** ✅ |
| **Q30** | 31.67 dB | 32.35 dB | **+0.67 dB** ✅ | 0.8891 | 0.9041 | **+0.015** ✅ |

**Moyenne globale** : **+0.87 dB PSNR** | **+0.030 SSIM**

## 🚀 Démarrage Rapide

### Prérequis

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (optionnel)

### Option 1 : Docker Compose (Recommandé)

```bash
# Cloner le repository
git clone https://github.com/AhmedMaaouia1/UnblurAI.git
cd UnblurAI

# Télécharger le modèle pré-entraîné (161 MB)
# Windows PowerShell:
Invoke-WebRequest -Uri "https://github.com/AhmedMaaouia1/UnblurAI/releases/download/v1.0.0/best_model.pth" `
  -OutFile "backend/models/best_model.pth"

# Linux/Mac:
curl -L -o backend/models/best_model.pth \
  https://github.com/AhmedMaaouia1/UnblurAI/releases/download/v1.0.0/best_model.pth

# Lancer avec Docker
docker compose up --build

# Accéder à l'application
# Frontend: http://localhost:5173
# API: http://localhost:8000
```

### Option 2 : Développement Local

**1. Télécharger le modèle :**

Le fichier modèle (`best_model.pth`, 161 MB) est disponible dans les [GitHub Releases](https://github.com/AhmedMaaouia1/UnblurAI/releases/latest).

```powershell
# Windows PowerShell
Invoke-WebRequest -Uri "https://github.com/AhmedMaaouia1/UnblurAI/releases/download/v1.0.0/best_model.pth" `
  -OutFile "backend/models/best_model.pth"
```

```bash
# Linux/Mac
curl -L -o backend/models/best_model.pth \
  https://github.com/AhmedMaaouia1/UnblurAI/releases/download/v1.0.0/best_model.pth
```

**2. Backend :**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**3. Frontend :**
```bash
cd frontend
npm install
npm run dev
```

## 📂 Structure du Projet

```
UnblurAI/
├── frontend/                 # React + Vite + TailwindCSS
│   ├── src/
│   │   ├── components/      # Composants réutilisables
│   │   ├── App.jsx          # Application principale
│   │   └── main.jsx         # Point d'entrée
│   ├── package.json
│   └── Dockerfile
│
├── backend/                  # FastAPI + PyTorch
│   ├── model.py             # Architecture U-Net Enhanced
│   ├── inference.py         # Pipeline d'inférence
│   ├── main.py              # API FastAPI
│   ├── requirements.txt
│   ├── Dockerfile
│   └── models/              # ⚠️ Téléchargez best_model.pth depuis Releases
│
├── docker-compose.yml        # Orchestration Docker
├── .gitignore
└── README.md
```

## 🔧 Architecture du Modèle

### U-Net Enhanced avec Optimisations

- **Input** : 4 canaux (RGB + Q/100 pour conditioning)
- **Output** : Delta résiduel (3 canaux RGB)
- **Reconstruction** : `restored = input + delta`
- **Paramètres** : 63.6M
- **Loss** : 0.5×Charbonnier + 0.3×MS-SSIM + 0.2×Edge

### Optimisations Clés

1. **Compression JPEG Aléatoire (Q ∈ [5, 30])** : Généralisation robuste
2. **Residual Learning** : Évite le sur-lissage
3. **Quality-Aware Conditioning** : Adaptation au niveau de compression
4. **Loss Multi-Composantes** : Préservation des détails et contours

## 🌐 API REST

### Endpoints

#### `POST /restore`

Restaure une image JPEG compressée.

**Paramètres:**
- `file` (multipart/form-data) : Image à restaurer (JPEG, PNG, WebP)
- `quality` (query, optional) : Qualité JPEG estimée (5-30, défaut: 10)

**Réponse:**
- Image restaurée en PNG

**Exemple cURL:**
```bash
curl -X POST "http://localhost:8000/restore?quality=10" \
  -F "file=@image_compressed.jpg" \
  -o restored.png
```

#### `POST /restore-jpeg`

Restaure et retourne un JPEG (fichier plus léger).

**Paramètres:**
- `file` (multipart/form-data) : Image à restaurer
- `quality_input` (query, optional) : Qualité JPEG estimée input (5-30, défaut: 10)
- `quality_output` (query, optional) : Qualité JPEG output (1-100, défaut: 95)

#### `GET /health`

Vérification de l'état de l'API.

## 🎓 Entraînement du Modèle

Le modèle a été entraîné sur le dataset **DIV2K** (800 images) avec les hyperparamètres suivants:

```python
# Configuration
BATCH_SIZE = 8
LEARNING_RATE = 1e-4
WEIGHT_DECAY = 1e-6
NUM_EPOCHS = 55
PATCH_SIZE = 256

# Augmentation
- Compression JPEG aléatoire Q∈[5,30]
- Flips horizontal/vertical
- Rotations 90°/180°/270°

# Scheduler
ReduceLROnPlateau(factor=0.5, patience=5)
```

**Durée d'entraînement** : 1h30 sur GPU NVIDIA T4

Pour entraîner votre propre modèle, consultez le notebook de training sur Google Colab (disponible dans les releases).

## ⚙️ Configuration

### Variables d'Environnement

**Backend (`backend/main.py`):**
```python
MODEL_PATH = "models/best_model.pth"      # Chemin du modèle
MAX_FILE_SIZE = 15 * 1024 * 1024          # Taille max upload (15 MB)
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
```

**Frontend (`frontend/src/App.jsx`):**
```javascript
const API_URL = "http://localhost:8000";  // URL de l'API backend
```

## 📝 TODO / Améliorations Futures

- [ ] Ajouter Perceptual Loss (VGG relu3_3) → **+0.15-0.25 dB**
- [ ] Augmenter patch size à 384×384 → **+0.10-0.15 dB**
- [ ] Ensemble de 3 modèles → **+0.20-0.30 dB**
- [ ] Fine-tuning séparé par qualité (Q5-15 vs Q15-30)
- [ ] Test-Time Augmentation (TTA)
- [ ] Support des images haute résolution (>4K)
- [ ] Batch processing API endpoint
- [ ] Interface web avec comparaison avant/après

## 🐛 Troubleshooting

### Le modèle ne charge pas

```bash
❌ Erreur: FileNotFoundError: models/best_model.pth
```

**Solution** : Téléchargez le modèle depuis les [Releases](https://github.com/AhmedMaaouia1/UnblurAI/releases/latest) et placez-le dans `backend/models/best_model.pth`.

```bash
❌ Erreur: size mismatch for enc1.0.weight
```

**Solution** : Assurez-vous d'utiliser un modèle entraîné avec `in_channels=4` (version optimisée).

### CUDA Out of Memory

**Solution** : Réduire la taille de l'image ou utiliser l'inférence par tuiles (automatique pour images >3000px).

### Images violettes/cyan après restauration

**Solution** : Vérifier la cohérence de normalisation `[-1, 1]` dans tout le pipeline.

## 📄 Licence

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- **Dataset** : [DIV2K](https://data.vision.ee.ethz.ch/cvl/DIV2K/) (NTIRE 2017)
- **Architecture** : Inspiré de U-Net et ResNet
- **Frameworks** : PyTorch, FastAPI, React

## 📧 Contact

Pour toute question ou suggestion :
- **Issues** : [GitHub Issues](https://github.com/votre-username/UnblurAI/issues)
- **Discussions** : [GitHub Discussions](https://github.com/votre-username/UnblurAI/discussions)

---

**Fait avec ❤️ et PyTorch**
