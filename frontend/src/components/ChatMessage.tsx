interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatMessageProps {
  message: Message;
}

function ChatMessage({ message }: ChatMessageProps) {
  return (
    <div className={`chat-message ${message.role}`}>
      <div className="message-avatar">
        {message.role === 'user' ? '👤' : '🤖'}
      </div>
      <div className="message-content">
        <div className="message-text">{message.content}</div>
      </div>
    </div>
  );
}

export default ChatMessage;
