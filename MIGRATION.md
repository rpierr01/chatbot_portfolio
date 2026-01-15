# Guide de Migration: Streamlit → React.js

Ce document explique les changements apportés lors de la conversion de l'application Streamlit vers React.js.

## 📋 Vue d'ensemble

### Avant (Streamlit)
- **Fichier principal**: `app.py`
- **Agent IA**: `agent.py`
- **Port**: 8501 (par défaut)
- **Commande**: `streamlit run app.py`

### Après (React.js)
- **Frontend**: `frontend/` (React + TypeScript)
- **Backend**: `backend/` (Node.js + Express)
- **Ports**: 
  - Backend: 3001
  - Frontend: 5173 (dev) ou 80/443 (prod)
- **Commande**: `npm run dev`

## 🔄 Correspondances des fichiers

| Streamlit | React.js | Description |
|-----------|----------|-------------|
| `app.py` | `frontend/src/App.tsx` | Application principale |
| `agent.py` | `backend/src/agent.ts` | Logique de l'agent IA |
| `styles.css` | `frontend/src/App.css` | Styles de l'interface |
| - | `backend/src/server.ts` | Serveur API (nouveau) |
| - | `frontend/src/components/*` | Composants React (nouveau) |

## 🎨 Correspondances des composants

### Interface utilisateur

| Streamlit | React.js | Notes |
|-----------|----------|-------|
| `st.set_page_config()` | `index.html` + `App.css` | Configuration de la page |
| `st.markdown()` avec HTML | Composants JSX | Rendu React natif |
| `st.sidebar` | `<Sidebar />` | Composant dédié |
| `st.chat_message()` | `<ChatMessage />` | Composant personnalisé |
| `st.chat_input()` | `<ChatInput />` | Composant contrôlé |
| `st.button()` | `<button onClick={}>` | Événement React |
| `st.spinner()` | `{isLoading && <Spinner />}` | État conditionnel |

### Gestion de l'état

| Streamlit | React.js | Notes |
|-----------|----------|-------|
| `st.session_state.messages` | `useState<Message[]>()` | Hook d'état local |
| `st.session_state.conversation_history` | `useState<Message[]>()` | Hook d'état local |
| `st.session_state.start_time` | `useState<Date>()` | Hook d'état local |
| `st.rerun()` | Mise à jour d'état automatique | React réagit aux changements |

### Logique métier

| Streamlit (Python) | React.js (TypeScript) | Notes |
|--------------------|----------------------|-------|
| `from agent import get_agent_response` | `axios.post('/api/chat')` | Appel API |
| `get_agent_response(prompt, history)` | `await getAgentResponse(...)` | Fonction async |
| `search_portfolio(query)` | Côté backend uniquement | Sécurité |
| `run_agent(...)` | `runAgent(...)` en Node.js | Même logique |

## 🔌 Nouvelles APIs

### Backend Endpoints

```typescript
// Health check
GET /api/health
Response: { status: 'ok', message: 'Backend is running' }

// Chat
POST /api/chat
Body: { message: string, history: Message[] }
Response: { response: string }
```

### Frontend Hooks

```typescript
// État des messages
const [messages, setMessages] = useState<Message[]>([]);

// État de chargement
const [isLoading, setIsLoading] = useState(false);

// Envoi de message
const handleSendMessage = async (message: string) => {
  // Logique d'envoi
};
```

## 📦 Gestion des dépendances

### Avant (Python)
```bash
pip install -r requirements.txt
```

**Dépendances**: `streamlit`, `openai-agents`, `upstash-vector`, etc.

### Après (Node.js)
```bash
npm run install:all
```

**Backend**: `express`, `openai`, `@upstash/vector`, `cors`, `dotenv`  
**Frontend**: `react`, `axios`, `vite`

## 🚀 Commandes de développement

### Streamlit
```bash
# Démarrer
streamlit run app.py

# Arrêter
Ctrl+C
```

### React.js
```bash
# Installer les dépendances
npm run install:all

# Démarrer (tout en un)
npm run dev

# Ou séparément
npm run dev:backend  # Terminal 1
npm run dev:frontend # Terminal 2

# Build
npm run build:all

# Arrêter
Ctrl+C dans chaque terminal
```

## 🔧 Configuration

### Variables d'environnement

**Avant (.env à la racine):**
```env
OPENAI_API_KEY=...
UPSTASH_VECTOR_REST_URL=...
UPSTASH_VECTOR_REST_TOKEN=...
```

**Après:**

**backend/.env:**
```env
OPENAI_API_KEY=...
UPSTASH_VECTOR_REST_URL=...
UPSTASH_VECTOR_REST_TOKEN=...
PORT=3001
```

**frontend/.env:**
```env
VITE_API_URL=http://localhost:3001
```

## 🎯 Avantages de React.js

### 1. Architecture séparée
- Frontend et backend indépendants
- Déploiement flexible
- Scalabilité améliorée

### 2. Performance
- Rendu optimisé avec Virtual DOM
- Chargement initial plus rapide
- Pas de rechargement de page

### 3. Expérience développeur
- Hot Module Replacement (HMR)
- TypeScript pour la sûreté des types
- Composants réutilisables
- Écosystème riche

### 4. Déploiement
- Multiple options (Vercel, Netlify, etc.)
- CDN pour le frontend
- Backend scalable indépendamment

### 5. Maintenance
- Code mieux organisé
- Tests plus faciles
- Documentation TypeScript intégrée

## 🔀 Différences comportementales

### 1. Rechargement de page
- **Streamlit**: La page se recharge à chaque interaction
- **React**: Mise à jour partielle uniquement

### 2. État de l'application
- **Streamlit**: Session state côté serveur
- **React**: État côté client (plus réactif)

### 3. Styles
- **Streamlit**: CSS + HTML string
- **React**: CSS modules + JSX

### 4. Communication API
- **Streamlit**: Appels directs Python
- **React**: HTTP REST API

## 📝 Checklist de migration

Pour migrer d'autres fonctionnalités Streamlit vers React:

- [ ] Identifier les composants Streamlit utilisés
- [ ] Créer les composants React équivalents
- [ ] Extraire la logique métier vers le backend
- [ ] Créer les endpoints API nécessaires
- [ ] Gérer l'état avec React Hooks
- [ ] Convertir les styles CSS
- [ ] Tester l'intégration
- [ ] Documenter les changements

## 🆘 Dépannage

### Problème: L'application Streamlit ne démarre plus
**Solution**: Les deux versions coexistent. Streamlit: `streamlit run app.py`, React: `npm run dev`

### Problème: Port déjà utilisé
**Solution**: 
- Streamlit: Modifier avec `--server.port 8502`
- React backend: Modifier `PORT` dans `.env`
- React frontend: Modifier dans `vite.config.ts`

### Problème: Les variables d'environnement ne fonctionnent pas
**Solution**: 
- Backend: Variables dans `backend/.env`
- Frontend: Variables préfixées par `VITE_` dans `frontend/.env`

### Problème: CORS errors
**Solution**: Le backend Express a déjà CORS configuré. Vérifier `VITE_API_URL`.

## 📚 Ressources supplémentaires

- [React Documentation](https://react.dev)
- [Vite Documentation](https://vitejs.dev)
- [Express Documentation](https://expressjs.com)
- [TypeScript Documentation](https://www.typescriptlang.org)
- [Axios Documentation](https://axios-http.com)

## 🎓 Formation recommandée

Si vous souhaitez personnaliser l'application React:

1. **React Basics**: Components, Props, State, Hooks
2. **TypeScript**: Types, Interfaces, Generics
3. **API Integration**: Fetch, Axios, Async/Await
4. **CSS Modern**: Flexbox, Grid, Animations
5. **Vite**: Configuration, Build, Plugins

## ✅ Conclusion

La migration vers React.js offre:
- ✅ Architecture moderne et scalable
- ✅ Meilleure performance
- ✅ Expérience utilisateur améliorée
- ✅ Flexibilité de déploiement
- ✅ Écosystème riche

L'application Streamlit originale reste disponible pour comparaison et peut coexister avec la version React.
