interface SidebarProps {
  messageCount: number;
  interactionCount: number;
  sessionDuration: number;
}

function Sidebar({ messageCount, interactionCount, sessionDuration }: SidebarProps) {
  // Note: Model name is hardcoded to match backend agent.ts configuration
  const modelName = "gpt-4.1-nano";
  
  return (
    <div className="sidebar">
      <div className="sidebar-content">
        <h3>🎯 SYSTÈME D'INFORMATION</h3>
        
        <div className="metric-card">
          <div className="metric-value pulse">{messageCount}</div>
          <div className="metric-label">MESSAGES ÉCHANGÉS</div>
        </div>
        
        <div className="metric-card">
          <div className="metric-value neon-text">{Math.floor(interactionCount)}</div>
          <div className="metric-label">INTERACTIONS</div>
        </div>
        
        <div className="metric-card">
          <div className="metric-value">{sessionDuration}</div>
          <div className="metric-label">MINUTES DE SESSION</div>
        </div>
        
        <hr className="sidebar-divider" />
        
        <h3>⚙️ CAPACITÉS DU SYSTÈME</h3>
        <div className="capabilities">
          <div className="capability-item">
            🔍 <span className="neon-text">Recherche Sémantique</span>
          </div>
          <div className="capability-item">
            💾 <span className="neon-text">Mémoire Conversationnelle</span>
          </div>
          <div className="capability-item">
            🧠 <span className="neon-text">IA Générative GPT-4.1</span>
          </div>
          <div className="capability-item">
            📊 <span className="neon-text">Analyse de Portfolio</span>
          </div>
          <div className="capability-item">
            ⚡ <span className="neon-text">Réponses en Temps Réel</span>
          </div>
        </div>
        
        <hr className="sidebar-divider" />
        
        <h3>📡 STATUT SYSTÈME</h3>
        <div className="status">
          <div className="status-indicator">
            🟢 <strong>OPÉRATIONNEL</strong>
          </div>
          <div className="status-details">
            Modèle: {modelName}<br />
            Latence: <span className="neon-text">Optimale</span>
          </div>
        </div>
        
        <hr className="sidebar-divider" />
        
        <div className="sidebar-footer">
          🔐 Interface Sécurisée | © 2026 Rémi AI
        </div>
      </div>
    </div>
  );
}

export default Sidebar;
