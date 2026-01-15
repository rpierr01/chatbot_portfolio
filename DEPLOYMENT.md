# Guide de Déploiement - RÉMI AI

Ce guide explique comment déployer l'application React.js RÉMI AI en production.

## 📋 Options de Déploiement

### Option 1: Déploiement Séparé (Recommandé)

#### Frontend (Vercel, Netlify, ou similaire)

**Vercel (Recommandé pour React):**

1. Créer un compte sur [Vercel](https://vercel.com)
2. Installer Vercel CLI:
   ```bash
   npm install -g vercel
   ```
3. Déployer le frontend:
   ```bash
   cd frontend
   vercel
   ```
4. Configurer les variables d'environnement dans Vercel:
   - `VITE_API_URL`: URL de votre backend (ex: https://api.votre-app.com)

**Netlify:**

1. Créer un compte sur [Netlify](https://netlify.com)
2. Build settings:
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/dist`
3. Variables d'environnement:
   - `VITE_API_URL`: URL de votre backend

#### Backend (Railway, Render, Heroku, ou similaire)

**Railway (Recommandé):**

1. Créer un compte sur [Railway](https://railway.app)
2. Créer un nouveau projet
3. Connecter votre repository GitHub
4. Configure Root Directory: `backend`
5. Variables d'environnement requises:
   ```
   OPENAI_API_KEY=votre_clé
   UPSTASH_VECTOR_REST_URL=votre_url
   UPSTASH_VECTOR_REST_TOKEN=votre_token
   PORT=3001
   ```
6. Railway détectera automatiquement Node.js et utilisera les scripts npm

**Render:**

1. Créer un compte sur [Render](https://render.com)
2. Créer un nouveau Web Service
3. Connecter votre repository
4. Configuration:
   - Root Directory: `backend`
   - Build Command: `npm install && npm run build`
   - Start Command: `npm start`
5. Ajouter les variables d'environnement

**Heroku:**

1. Créer un compte sur [Heroku](https://heroku.com)
2. Créer une nouvelle app
3. Installer Heroku CLI et se connecter
4. Déployer:
   ```bash
   cd backend
   heroku git:remote -a votre-app-name
   git subtree push --prefix backend heroku main
   ```
5. Configurer les variables d'environnement:
   ```bash
   heroku config:set OPENAI_API_KEY=votre_clé
   heroku config:set UPSTASH_VECTOR_REST_URL=votre_url
   heroku config:set UPSTASH_VECTOR_REST_TOKEN=votre_token
   ```

### Option 2: Déploiement Monolithique (VPS)

**DigitalOcean, AWS EC2, ou VPS similaire:**

1. **Préparer le serveur:**
   ```bash
   # Installer Node.js 18+
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt-get install -y nodejs
   
   # Installer nginx
   sudo apt-get install nginx
   ```

2. **Cloner et configurer:**
   ```bash
   git clone https://github.com/votre-username/chatbot_portfolio.git
   cd chatbot_portfolio
   
   # Configurer les variables d'environnement
   cp backend/.env.example backend/.env
   nano backend/.env  # Éditer avec vos clés
   
   # Installer les dépendances
   npm run install:all
   
   # Build
   npm run build:all
   ```

3. **Configurer PM2 (Process Manager):**
   ```bash
   sudo npm install -g pm2
   
   # Démarrer le backend
   cd backend
   pm2 start dist/server.js --name "remi-backend"
   pm2 save
   pm2 startup
   ```

4. **Configurer Nginx:**
   ```nginx
   # /etc/nginx/sites-available/remi-ai
   server {
       listen 80;
       server_name votre-domaine.com;
   
       # Frontend
       location / {
           root /path/to/chatbot_portfolio/frontend/dist;
           try_files $uri $uri/ /index.html;
       }
   
       # Backend API
       location /api {
           proxy_pass http://localhost:3001;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```
   
   ```bash
   sudo ln -s /etc/nginx/sites-available/remi-ai /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

5. **Configurer SSL avec Certbot:**
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot --nginx -d votre-domaine.com
   ```

### Option 3: Docker (Pour tous les environnements)

**Créer Dockerfile pour le backend:**

```dockerfile
# backend/Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3001
CMD ["npm", "start"]
```

**Créer Dockerfile pour le frontend:**

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Docker Compose:**

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "3001:3001"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - UPSTASH_VECTOR_REST_URL=${UPSTASH_VECTOR_REST_URL}
      - UPSTASH_VECTOR_REST_TOKEN=${UPSTASH_VECTOR_REST_TOKEN}
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

**Déployer avec Docker:**
```bash
docker-compose up -d
```

## 🔒 Sécurité en Production

1. **HTTPS obligatoire** - Utilisez toujours SSL/TLS
2. **Variables d'environnement** - Ne jamais committer les clés API
3. **CORS** - Configurer correctement les origines autorisées dans le backend
4. **Rate Limiting** - Ajouter une limitation de requêtes
5. **Monitoring** - Utiliser des outils comme Sentry pour le tracking d'erreurs

## 📊 Monitoring et Logs

**Backend logs avec PM2:**
```bash
pm2 logs remi-backend
pm2 monit
```

**Sentry (Recommandé):**
1. Créer un compte sur [Sentry](https://sentry.io)
2. Ajouter Sentry au backend:
   ```bash
   npm install @sentry/node
   ```
3. Configurer dans server.ts

## 🔄 Mises à Jour

**Avec Git:**
```bash
git pull origin main
npm run build:all
pm2 restart remi-backend
```

**Avec Docker:**
```bash
git pull origin main
docker-compose down
docker-compose up -d --build
```

## 🆘 Dépannage

### Le backend ne démarre pas
- Vérifier les logs: `pm2 logs` ou `docker logs`
- Vérifier les variables d'environnement
- Vérifier que le port 3001 n'est pas déjà utilisé

### Le frontend ne se connecte pas au backend
- Vérifier la variable `VITE_API_URL`
- Vérifier la configuration CORS du backend
- Vérifier les logs du navigateur (F12)

### Erreurs API OpenAI
- Vérifier la clé API
- Vérifier les quotas et limites
- Vérifier la connexion réseau

## 📝 Checklist Avant Déploiement

- [ ] Variables d'environnement configurées
- [ ] Build frontend réussi (`npm run build`)
- [ ] Build backend réussi (`npm run build`)
- [ ] Tests de l'API backend
- [ ] Configuration CORS correcte
- [ ] SSL/HTTPS configuré
- [ ] Monitoring configuré
- [ ] Backups configurés (base de données si applicable)

## 🔗 Ressources Utiles

- [Vercel Docs](https://vercel.com/docs)
- [Railway Docs](https://docs.railway.app)
- [Render Docs](https://render.com/docs)
- [PM2 Docs](https://pm2.keymetrics.io/docs)
- [Nginx Docs](https://nginx.org/en/docs)
