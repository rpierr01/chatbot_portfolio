#!/bin/bash

# Script pour démarrer l'application React.js (Backend + Frontend)

echo "🚀 Démarrage de l'application RÉMI AI..."
echo ""

# Vérifier si les dépendances sont installées
if [ ! -d "backend/node_modules" ] || [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installation des dépendances..."
    npm run install:all
    echo ""
fi

# Vérifier si les fichiers .env existent
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Attention: backend/.env n'existe pas!"
    echo "   Créez le fichier backend/.env en copiant backend/.env.example"
    echo "   et ajoutez vos clés API."
    exit 1
fi

echo "✅ Tout est prêt!"
echo ""
echo "🔹 Backend sera accessible sur: http://localhost:3001"
echo "🔹 Frontend sera accessible sur: http://localhost:5173"
echo ""
echo "Pour arrêter l'application, utilisez Ctrl+C dans chaque terminal"
echo ""

# Lancer le backend et le frontend dans des terminaux séparés
echo "📡 Démarrage du backend..."
echo "   Ouvrez un nouveau terminal et exécutez: npm run dev:backend"
echo ""
echo "🎨 Démarrage du frontend..."
echo "   Ouvrez un autre terminal et exécutez: npm run dev:frontend"
