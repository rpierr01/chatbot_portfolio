interface HeaderProps {
  onNewConversation: () => void;
}

function Header({ onNewConversation }: HeaderProps) {
  return (
    <div className="header-section">
      <div className="tech-header">
        <h1>🤖 RÉMI AI - JUMEAU VIRTUEL</h1>
        <p className="tech-subtitle">
          ⚡ Intelligence Artificielle | Science des Données | Portfolio Interactif
        </p>
      </div>
      
      <div className="controls">
        <button 
          className="new-conversation-btn" 
          onClick={onNewConversation}
        >
          🔄 NOUVELLE CONVERSATION
        </button>
      </div>
    </div>
  );
}

export default Header;
