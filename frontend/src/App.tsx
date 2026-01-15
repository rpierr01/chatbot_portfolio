import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';
import Header from './components/Header';
import ChatMessage from './components/ChatMessage';
import Sidebar from './components/Sidebar';
import ChatInput from './components/ChatInput';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationHistory, setConversationHistory] = useState<Message[]>([]);
  const [startTime] = useState<Date>(new Date());
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleNewConversation = () => {
    setMessages([]);
    setConversationHistory([]);
  };

  const handleSendMessage = async (message: string) => {
    if (!message.trim()) return;

    // Add user message to UI
    const userMessage: Message = { role: 'user', content: message };
    setMessages(prev => [...prev, userMessage]);

    setIsLoading(true);

    try {
      // Call backend API
      const response = await axios.post(`${API_URL}/api/chat`, {
        message: message,
        history: conversationHistory,
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.response,
      };

      // Add assistant message to UI
      setMessages(prev => [...prev, assistantMessage]);

      // Update conversation history
      setConversationHistory(prev => [
        ...prev,
        userMessage,
        assistantMessage,
      ]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Désolé, une erreur s\'est produite. Veuillez réessayer.',
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const getSessionDuration = () => {
    const now = new Date();
    const diffMs = now.getTime() - startTime.getTime();
    return Math.floor(diffMs / 60000);
  };

  return (
    <div className="app">
      <Sidebar
        messageCount={messages.length}
        interactionCount={conversationHistory.length / 2}
        sessionDuration={getSessionDuration()}
      />
      
      <div className="main-content">
        <Header onNewConversation={handleNewConversation} />
        
        <div className="chat-container">
          <div className="messages-container">
            {messages.map((message, index) => (
              <ChatMessage key={index} message={message} />
            ))}
            {isLoading && (
              <div className="loading-indicator">
                <div className="spinner"></div>
                <span>🔮 Analyse en cours...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          
          <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
}

export default App;
