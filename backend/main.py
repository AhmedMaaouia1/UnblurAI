"""
API FastAPI pour la restauration d'images avec U-Net.
"""

import os
import io
import sys
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import torch
from PIL import Image

from model import load_model
from inference import restore_image


# Configuration
MODEL_PATH = "models/best_model.pth"
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# Initialisation de l'application
app = FastAPI(
    title="UnblurAI API",
    description="API de restauration d'images avec U-Net",
    version="1.0.0"
)

# Configuration CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales
model = None
device = None


@app.on_event("startup")
async def startup_event():
    """
    Initialisation au démarrage de l'application.
    Charge le modèle et détecte le device disponible.
    """
    global model, device
    
    print("=" * 60)
    print("🚀 Démarrage de UnblurAI API")
    print("=" * 60)
    
    # Détection du device
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"✅ GPU détecté : {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device("cpu")
        print("⚠️  Aucun GPU détecté, utilisation du CPU")
    
    # Vérification de l'existence du modèle
    if not os.path.exists(MODEL_PATH):
        print("\n" + "=" * 60)
        print("❌ ERREUR : Fichier modèle introuvable !")
        print("=" * 60)
        print(f"Le fichier '{MODEL_PATH}' n'existe pas.")
        print("\n📋 Instructions :")
        print(f"  1. Placez votre fichier 'best_model.pth' dans le dossier 'models/'")
        print(f"  2. Chemin attendu : {os.path.abspath(MODEL_PATH)}")
        print(f"  3. Redémarrez l'application")
        print("=" * 60 + "\n")
        
        # L'application continuera de tourner mais renverra une erreur sur /restore
        model = None
        return
    
    # Chargement du modèle
    try:
        print(f"📦 Chargement du modèle depuis '{MODEL_PATH}'...")
        model = load_model(MODEL_PATH, device)
        print("✅ Modèle chargé avec succès !")
        
        # Afficher les informations du modèle
        num_params = sum(p.numel() for p in model.parameters())
        print(f"📊 Nombre de paramètres : {num_params:,}")
        
    except Exception as e:
        print(f"❌ Erreur lors du chargement du modèle : {e}")
        model = None
        return
    
    print("=" * 60)
    print("✅ UnblurAI API prête !")
    print(f"📡 Écoutant sur http://0.0.0.0:8000")
    print("=" * 60 + "\n")


@app.get("/")
async def root():
    """
    Endpoint racine - Vérification que l'API fonctionne.
    """
    if model is None:
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "message": "UnblurAI API - Modèle non chargé",
                "detail": f"Le fichier modèle '{MODEL_PATH}' est introuvable ou invalide."
            }
        )
    
    return {
        "status": "ok",
        "message": "UnblurAI API running",
        "version": "1.0.0",
        "device": str(device),
        "model_loaded": model is not None
    }


@app.get("/health")
async def health():
    """
    Endpoint de santé pour vérifier l'état de l'API.
    """
    return {
        "status": "healthy" if model is not None else "unhealthy",
        "model_loaded": model is not None,
        "device": str(device) if device else None
    }


@app.post("/restore")
async def restore_endpoint(file: UploadFile = File(...), quality: int = 5):
    """
    Endpoint principal de restauration d'images.
    
    🆕 MODÈLE OPTIMISÉ:
    - Paramètre quality (5-30) pour le conditioning
    - Permet au modèle d'adapter son traitement
    
    Args:
        file: Fichier image uploadé (JPEG, PNG, WebP)
        quality: Qualité JPEG estimée (5-30, défaut: 10)
    
    Returns:
        Image restaurée en PNG
    
    Raises:
        HTTPException: En cas d'erreur de validation ou de traitement
    """
    # Vérifier que le modèle est chargé
    if model is None:
        raise HTTPException(
            status_code=503,
            detail=f"Le modèle n'est pas chargé. Vérifiez que '{MODEL_PATH}' existe."
        )
    
    # Validation du paramètre quality (5-30)
    quality = max(5, min(30, quality))
    
    # Vérifier l'extension du fichier
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Format de fichier non supporté. Formats acceptés : {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Lire le contenu du fichier
    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erreur lors de la lecture du fichier : {str(e)}"
        )
    
    # Vérifier la taille du fichier
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Fichier trop volumineux. Taille maximale : {MAX_FILE_SIZE // (1024*1024)} MB"
        )
    
    # Décoder l'image
    try:
        image = Image.open(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Impossible de décoder l'image : {str(e)}"
        )
    
    # Vérifier que l'image n'est pas vide
    if image.size[0] == 0 or image.size[1] == 0:
        raise HTTPException(
            status_code=400,
            detail="L'image est vide ou invalide"
        )
    
    print(f"📸 Image reçue : {image.size[0]}x{image.size[1]} ({file.filename})")
    print(f"🎯 Quality conditioning : Q={quality}")
    
    # Restauration de l'image avec quality conditioning
    try:
        restored_image = restore_image(model, image, device, quality=quality)
        print(f"✅ Image restaurée avec succès")
        
    except torch.cuda.OutOfMemoryError:
        raise HTTPException(
            status_code=507,
            detail="Mémoire GPU insuffisante. Essayez avec une image plus petite."
        )
    except Exception as e:
        print(f"❌ Erreur lors de la restauration : {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la restauration : {str(e)}"
        )
    
    # Convertir l'image restaurée en bytes (PNG pour éviter la perte de qualité)
    output_buffer = io.BytesIO()
    restored_image.save(output_buffer, format="PNG", optimize=True)
    output_buffer.seek(0)
    
    # Retourner l'image
    return StreamingResponse(
        output_buffer,
        media_type="image/png",
        headers={
            "Content-Disposition": f"inline; filename=restored_{file.filename.rsplit('.', 1)[0]}.png"
        }
    )


@app.post("/restore-jpeg")
async def restore_jpeg_endpoint(file: UploadFile = File(...), quality_output: int = 95, quality_input: int = 5):
    """
    Endpoint alternatif qui retourne un JPEG (fichier plus léger).
    
    🆕 MODÈLE OPTIMISÉ:
    - quality_input: Qualité JPEG estimée de l'input (5-30) pour conditioning
    - quality_output: Qualité JPEG du fichier de sortie (1-100)
    
    Args:
        file: Fichier image uploadé
        quality_output: Qualité JPEG de sortie (1-100, défaut: 95)
        quality_input: Qualité JPEG estimée de l'input (5-30, défaut: 10)
    
    Returns:
        Image restaurée en JPEG
    """
    if model is None:
        raise HTTPException(
            status_code=503,
            detail=f"Le modèle n'est pas chargé. Vérifiez que '{MODEL_PATH}' existe."
        )
    
    # Validation des qualités
    quality_output = max(1, min(100, quality_output))
    quality_input = max(5, min(30, quality_input))
    
    # Réutiliser la logique de restore_endpoint
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Format non supporté")
    
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Fichier trop volumineux")
    
    try:
        image = Image.open(io.BytesIO(contents))
        restored_image = restore_image(model, image, device, quality=quality_input)
        
        # Sauvegarder en JPEG
        output_buffer = io.BytesIO()
        restored_image.save(output_buffer, format="JPEG", quality=quality_output, optimize=True)
        output_buffer.seek(0)
        
        return StreamingResponse(
            output_buffer,
            media_type="image/jpeg",
            headers={
                "Content-Disposition": f"inline; filename=restored_{file.filename.rsplit('.', 1)[0]}.jpg"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
