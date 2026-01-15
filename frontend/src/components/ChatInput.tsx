import { useState, type KeyboardEvent } from 'react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled: boolean;
}

function ChatInput({ onSendMessage, disabled }: ChatInputProps) {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = () => {
    if (inputValue.trim() && !disabled) {
      onSendMessage(inputValue);
      setInputValue('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="chat-input-container">
      <input
        type="text"
        className="chat-input"
        placeholder="💬 Posez votre question à Rémi..."
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyPress={handleKeyPress}
        disabled={disabled}
      />
      <button
        className="send-button"
        onClick={handleSubmit}
        disabled={disabled || !inputValue.trim()}
      >
        ➤
      </button>
    </div>
  );
}

export default ChatInput;
