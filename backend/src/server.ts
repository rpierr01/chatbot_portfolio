import express, { Request, Response } from 'express';
import cors from 'cors';
import { getAgentResponse } from './agent';

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

interface ChatRequest {
  message: string;
  history: ChatMessage[];
}

// Health check endpoint
app.get('/api/health', (req: Request, res: Response) => {
  res.json({ status: 'ok', message: 'Backend is running' });
});

// Chat endpoint
app.post('/api/chat', async (req: Request, res: Response) => {
  try {
    const { message, history = [] }: ChatRequest = req.body;

    if (!message || typeof message !== 'string') {
      return res.status(400).json({ error: 'Message is required and must be a string' });
    }

    // Get response from agent
    const response = await getAgentResponse(message, history);

    res.json({ response });
  } catch (error) {
    console.error('Error in /api/chat:', error);
    res.status(500).json({ 
      error: 'Internal server error', 
      message: error instanceof Error ? error.message : 'Unknown error' 
    });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 Backend server is running on http://localhost:${PORT}`);
  console.log(`📡 Health check: http://localhost:${PORT}/api/health`);
  console.log(`💬 Chat endpoint: http://localhost:${PORT}/api/chat`);
});
