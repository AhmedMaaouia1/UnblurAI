# Contribution Guidelines

Merci de votre intérêt pour contribuer à UnblurAI ! 🎉

## Comment Contribuer

### 1. Signaler un Bug

Si vous trouvez un bug, ouvrez une [issue](https://github.com/votre-username/UnblurAI/issues) avec :
- Description claire du problème
- Steps to reproduce
- Comportement attendu vs comportement actuel
- Screenshots si applicable
- Environnement (OS, Python version, GPU/CPU, etc.)

### 2. Proposer une Amélioration

Pour les nouvelles fonctionnalités :
1. Ouvrez une [discussion](https://github.com/votre-username/UnblurAI/discussions)
2. Expliquez le cas d'usage
3. Proposez une implémentation

### 3. Soumettre une Pull Request

#### Setup

```bash
# Fork le projet
git clone https://github.com/votre-username/UnblurAI.git
cd UnblurAI

# Créer une branche
git checkout -b feature/nom-de-votre-feature

# Installer les dépendances
cd backend && pip install -r requirements.txt
cd ../frontend && npm install
```

#### Développement

- Suivez les conventions de code existantes
- Ajoutez des tests si applicable
- Commentez le code complexe
- Mettez à jour la documentation

#### Commit

Utilisez des messages de commit clairs :
```
feat: Ajouter support des images PNG haute résolution
fix: Corriger le bug de normalisation sur CPU
docs: Mettre à jour les instructions d'installation
refactor: Optimiser le pipeline d'inférence
```

#### Submit

```bash
git add .
git commit -m "feat: Description de votre contribution"
git push origin feature/nom-de-votre-feature
```

Puis ouvrez une Pull Request sur GitHub.

## Code Style

### Python (Backend)
- PEP 8
- Type hints recommandés
- Docstrings pour les fonctions publiques

### JavaScript (Frontend)
- ESLint + Prettier
- Composants fonctionnels React
- Props destructuring

## Tests

```bash
# Backend
pytest tests/

# Frontend
npm test
```

## Questions ?

N'hésitez pas à ouvrir une [discussion](https://github.com/votre-username/UnblurAI/discussions) !

---

**Merci de contribuer à UnblurAI ! 🚀**
