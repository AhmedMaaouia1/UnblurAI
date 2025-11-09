# 🚨 Solution : Nettoyer l'historique Git et Push sur GitHub

## ⚠️ Problème Identifié

Le fichier `backend/models/best_model.pth` (161 MB) a été commité dans l'historique Git.
GitHub refuse les fichiers > 100 MB.

## ✅ Solution : Reset Complet + Push Propre

### **Étape 1 : Sauvegarder le modèle**

```powershell
# Sauvegarder le modèle en dehors du projet
Copy-Item backend/models/best_model.pth ../best_model_backup.pth
```

### **Étape 2 : Nettoyer TOUT l'historique Git**

```powershell
# Supprimer complètement l'historique Git
Remove-Item -Recurse -Force .git

# Réinitialiser Git
git init
```

### **Étape 3 : Vérifier le .gitignore**

Le `.gitignore` contient déjà :
```
backend/models/*.pth
backend/models/**/*.pth
```

✅ Tous les fichiers `.pth` seront exclus automatiquement !

### **Étape 4 : Commit sans le modèle**

```powershell
# Ajouter tous les fichiers (sauf .pth grâce au .gitignore)
git add .

# Vérifier qu'aucun .pth n'est tracké
git status | Select-String ".pth"
# ⚠️ Devrait être VIDE !

# Commit
git commit -m "Initial commit: UnblurAI - JPEG artifact removal with U-Net Enhanced

- Model: 63.6M parameters, 4-channel input (RGB + Q/100)
- Performance: +0.87 dB PSNR average across Q5-Q30
- Architecture: Residual learning + multi-component loss (Charbonnier + MS-SSIM + Edge)
- Stack: FastAPI backend + React frontend + Docker Compose
- Features: /restore and /restore-jpeg endpoints with quality-aware processing
- Training: 55 epochs on DIV2K, 1h30 on T4 GPU
- Model weights available in GitHub Releases (161 MB)
- 4 optimizations: random compression, residual learning, combined loss, Q-conditioning"
```

### **Étape 5 : Push sur GitHub**

```powershell
# Lier au repository GitHub
git remote add origin https://github.com/AhmedMaaouia1/UnblurAI.git

# Push
git branch -M main
git push -u origin main --force
```

✅ **Cette fois, ça va marcher !** (aucun fichier > 100 MB)

### **Étape 6 : Restaurer le modèle localement**

```powershell
# Restaurer le modèle pour le développement local
Copy-Item ../best_model_backup.pth backend/models/best_model.pth
```

### **Étape 7 : Créer une GitHub Release avec le modèle**

1. Allez sur [GitHub Releases](https://github.com/AhmedMaaouia1/UnblurAI/releases)
2. Cliquez **"Create a new release"**
3. **Tag** : `v1.0.0`
4. **Title** : `UnblurAI v1.0 - Initial Release`
5. **Description** :

```markdown
## 🎯 UnblurAI v1.0 - JPEG Artifact Removal Model

### 📊 Performance

Résultats sur DIV2K (50 images de validation):

| Qualité | PSNR Avant | PSNR Après | **Gain** | SSIM Avant | SSIM Après | **Gain** |
|---------|-----------|-----------|---------|-----------|-----------|---------|
| Q5  | 24.47 dB | 25.48 dB | **+1.01 dB** | 0.6904 | 0.7378 | **+0.047** |
| Q10 | 27.62 dB | 28.62 dB | **+1.00 dB** | 0.7922 | 0.8282 | **+0.036** |
| Q20 | 30.26 dB | 31.06 dB | **+0.80 dB** | 0.8603 | 0.8820 | **+0.022** |
| Q30 | 31.67 dB | 32.35 dB | **+0.67 dB** | 0.8891 | 0.9041 | **+0.015** |

**Moyenne** : **+0.87 dB PSNR** | **+0.030 SSIM**

### 🔧 Détails Techniques

- **Architecture** : U-Net Enhanced
- **Paramètres** : 63,585,731 (63.6M)
- **Input** : 4 canaux (RGB + Q/100 conditioning)
- **Output** : Delta résiduel (3 canaux RGB)
- **Loss** : 0.5×Charbonnier + 0.3×MS-SSIM + 0.2×Edge
- **Training** : 55 epochs sur DIV2K (800 images)
- **Durée** : 1h30 sur NVIDIA T4 GPU

### 🚀 Optimisations Appliquées

1. **Compression JPEG aléatoire** (Q ∈ [5, 30])
2. **Residual learning** (restored = input + delta)
3. **Loss multi-composantes** (Charbonnier + MS-SSIM + Edge)
4. **Quality-aware conditioning** (canal Q/100)

### 📥 Installation

1. Téléchargez `best_model.pth` ci-dessous (161 MB)
2. Placez-le dans `backend/models/best_model.pth`
3. Lancez l'application :

```bash
docker compose up --build
```

### 📚 Documentation

Consultez le [README](https://github.com/AhmedMaaouia1/UnblurAI) pour plus de détails.
```

6. **Attachez le fichier** `best_model.pth` (161 MB)
7. **Publish Release** ✅

---

## 🎉 Résumé

**Avant** :
- ❌ Repository contenait `best_model.pth` (161 MB)
- ❌ Git refusait le push (> 100 MB)

**Après** :
- ✅ Repository < 10 MB (seulement le code)
- ✅ Modèle disponible via GitHub Releases
- ✅ `.gitignore` empêche les futurs commits de `.pth`
- ✅ `backend/models/README.md` guide les utilisateurs
- ✅ `README.md` principal mis à jour avec instructions de téléchargement

**Pour les utilisateurs** :
```powershell
# 1. Cloner le projet
git clone https://github.com/AhmedMaaouia1/UnblurAI.git
cd UnblurAI

# 2. Télécharger le modèle
Invoke-WebRequest -Uri "https://github.com/AhmedMaaouia1/UnblurAI/releases/download/v1.0.0/best_model.pth" `
  -OutFile "backend/models/best_model.pth"

# 3. Lancer
docker compose up --build
```

---

## 📝 Commandes Complètes (Copier-Coller)

```powershell
# Étape 1 : Sauvegarder le modèle
Copy-Item backend/models/best_model.pth ../best_model_backup.pth

# Étape 2 : Reset Git
Remove-Item -Recurse -Force .git
git init

# Étape 3 : Commit sans modèle
git add .
git commit -m "Initial commit: UnblurAI - JPEG artifact removal with U-Net Enhanced

- Model: 63.6M parameters, 4-channel input (RGB + Q/100)
- Performance: +0.87 dB PSNR average across Q5-Q30
- Architecture: Residual learning + multi-component loss
- Stack: FastAPI backend + React frontend + Docker Compose
- Model weights available in GitHub Releases (161 MB)"

# Étape 4 : Push
git remote add origin https://github.com/AhmedMaaouia1/UnblurAI.git
git branch -M main
git push -u origin main --force

# Étape 5 : Restaurer le modèle localement
Copy-Item ../best_model_backup.pth backend/models/best_model.pth

# Étape 6 : Créer la release sur GitHub avec best_model.pth
```

🚀 **Vous êtes prêt à push !**
