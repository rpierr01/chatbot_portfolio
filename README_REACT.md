# RÉMI AI - Jumeau Virtuel (React.js)

Application de chatbot portfolio convertie de Streamlit vers React.js avec backend Node.js/Express.

## 🎯 Description

Cette application permet d'interagir avec un jumeau virtuel de Rémi, étudiant en Science des Données. Le chatbot utilise :
- **RAG (Retrieval-Augmented Generation)** avec Upstash Vector pour la recherche sémantique
- **GPT-4.1-nano** d'OpenAI pour les réponses intelligentes
- **Mémoire conversationnelle** pour maintenir le contexte

## 🏗️ Architecture

L'application est composée de deux parties :

### Backend (Node.js + Express + TypeScript)
- API REST pour gérer les requêtes du chatbot
- Intégration avec OpenAI et Upstash Vector
- Port par défaut : 3001

### Frontend (React + TypeScript + Vite)
- Interface utilisateur moderne avec design tech/néon
- Gestion d'état avec React Hooks
- Port par défaut : 5173

## 📋 Prérequis

- **Node.js** 18+ ([Download Node.js](https://nodejs.org/))
- **npm** ou **yarn**
- Compte **Upstash** avec un Vector Index configuré
- Clé API **OpenAI** avec accès au modèle gpt-4.1-nano

## 🚀 Installation

### 1. Configuration de la base de données vectorielle Upstash

Créer un compte sur [Upstash](https://console.upstash.com/auth/sign-up) et créer un Vector Index avec :
- **Région** : Ireland (eu-west-1)
- **Type** : Hybrid
- **Dense Embedding Model** : BAAI/bge-m3
- **Metric** : COSINE
- **Sparse Embedding Model** : BM25

### 2. Cloner le dépôt et installer les dépendances

```bash
# Backend
cd backend
npm install
cp .env.example .env
# Éditer .env et ajouter vos clés API

# Frontend
cd ../frontend
npm install
cp .env.example .env
# Éditer .env si besoin (URL de l'API)
```

### 3. Configuration des variables d'environnement

#### Backend (.env)
```env
OPENAI_API_KEY="votre_clé_openai"
UPSTASH_VECTOR_REST_URL="votre_url_upstash"
UPSTASH_VECTOR_REST_TOKEN="votre_token_upstash"
PORT=3001
```

#### Frontend (.env)
```env
VITE_API_URL=http://localhost:3001
```

## 🏃 Lancement de l'application

### Mode Développement

**Terminal 1 - Backend :**
```bash
cd backend
npm run dev
```

**Terminal 2 - Frontend :**
```bash
cd frontend
npm run dev
```

L'application sera accessible sur `http://localhost:5173`

### Mode Production

**Backend :**
```bash
cd backend
npm run build
npm start
```

**Frontend :**
```bash
cd frontend
npm run build
npm run preview
```

## 📦 Structure du projet

```
chatbot_portfolio/
├── backend/
│   ├── src/
│   │   ├── agent.ts       # Logique de l'agent IA
│   │   └── server.ts      # Serveur Express
│   ├── .env.example
│   ├── package.json
│   └── tsconfig.json
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.tsx
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   └── Sidebar.tsx
│   │   ├── App.tsx
│   │   ├── App.css
│   │   └── main.tsx
│   ├── .env.example
│   ├── package.json
│   └── vite.config.ts
├── data/                   # Fichiers markdown du portfolio
├── app.py                  # Ancienne version Streamlit
└── README_REACT.md
```

## 🎨 Fonctionnalités

- ✅ Interface de chat moderne avec design tech/néon
- ✅ Recherche sémantique dans le portfolio
- ✅ Mémoire conversationnelle
- ✅ Métriques de session en temps réel
- ✅ Nouvelle conversation
- ✅ Loading states
- ✅ Design responsive

## 🔧 Scripts disponibles

### Backend
- `npm run dev` - Lance le serveur en mode développement avec hot reload
- `npm run build` - Compile le TypeScript
- `npm start` - Lance le serveur en production

### Frontend
- `npm run dev` - Lance le serveur de développement Vite
- `npm run build` - Génère le build de production
- `npm run preview` - Prévisualise le build de production

## 🐛 Dépannage

### Le backend ne démarre pas
- Vérifier que toutes les variables d'environnement sont définies dans `.env`
- Vérifier que le port 3001 n'est pas déjà utilisé

### Le frontend ne peut pas se connecter au backend
- Vérifier que le backend est lancé sur le port 3001
- Vérifier la variable `VITE_API_URL` dans le `.env` du frontend
- Vérifier les erreurs CORS dans la console du navigateur

### Erreurs d'API OpenAI
- Vérifier que la clé API est valide
- Vérifier l'accès au modèle `gpt-4.1-nano`

## 📝 Différences avec la version Streamlit

| Fonctionnalité | Streamlit | React.js |
|----------------|-----------|----------|
| Langage | Python | TypeScript |
| Framework | Streamlit | React + Vite |
| Backend | Intégré | Express séparé |
| State Management | Session state | React Hooks |
| Styling | CSS + HTML string | CSS modules |
| Hot Reload | ✅ | ✅ |
| Production Ready | ✅ | ✅ |

## 🚀 Déploiement

### Frontend (Vercel, Netlify, etc.)
```bash
cd frontend
npm run build
# Déployer le dossier dist/
```

### Backend (Heroku, Railway, etc.)
```bash
cd backend
npm run build
# Configurer les variables d'environnement
# Déployer avec npm start
```

## 📄 Licence

Projet académique - © 2026 Rémi AI

## 🙋 Support

Pour toute question ou problème, veuillez consulter la documentation ou ouvrir une issue.
