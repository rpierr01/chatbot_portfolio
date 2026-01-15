import { Index } from '@upstash/vector';
import OpenAI from 'openai';
import { config } from 'dotenv';

config();

interface Message {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

/**
 * Recherche des informations dans la base de données vectorielle Upstash.
 */
export async function searchPortfolio(query: string): Promise<string> {
  try {
    const url = process.env.UPSTASH_VECTOR_REST_URL;
    const token = process.env.UPSTASH_VECTOR_REST_TOKEN;

    if (!url || !token) {
      return '';
    }

    const index = new Index({
      url,
      token,
    });

    // Recherche sémantique (RAG)
    const results = await index.query({
      data: query,
      topK: 3,
      includeMetadata: true,
    });

    if (!results || results.length === 0) {
      return '';
    }

    // Extraction du texte depuis les métadonnées
    const contextSegments: string[] = results
      .filter(res => res.metadata && typeof res.metadata === 'object')
      .map(res => {
        const metadata = res.metadata as { text?: string };
        return metadata.text || '';
      })
      .filter(text => text !== '');

    return contextSegments.join('\n\n');
  } catch (error) {
    console.error(`Note : Erreur lors de la connexion à Upstash (${error}). Le contexte ne sera pas chargé.`);
    return '';
  }
}

/**
 * Exécute l'agent en prenant en compte l'historique de conversation.
 */
async function runAgent(
  userInput: string,
  instructions: string,
  apiKey: string,
  modelName: string,
  history: Message[]
): Promise<string> {
  // 1. Récupération du contexte (RAG)
  const context = await searchPortfolio(userInput);

  // 2. Construction du message système
  let systemContent = instructions;
  if (context) {
    systemContent += `\n\nCONTEXTE DU PORTFOLIO (utilise ces infos si pertinentes) :\n${context}`;
  }

  const messages: Message[] = [{ role: 'system', content: systemContent }];

  // 3. Injection de l'historique complet (Mémoire)
  messages.push(...history);

  // 4. Ajout de la nouvelle question utilisateur
  messages.push({ role: 'user', content: userInput });

  // 5. Appel API
  const client = new OpenAI({ apiKey });

  try {
    const response = await client.chat.completions.create({
      model: modelName,
      messages: messages,
    });

    return response.choices[0]?.message?.content || 'Pas de réponse.';
  } catch (error) {
    console.error('Erreur lors de l\'appel à l\'API OpenAI:', error);
    throw new Error(`Erreur lors de l'appel à l'API OpenAI : ${error}`);
  }
}

/**
 * Initialise l'agent IA avec les paramètres spécifiques.
 */
export async function getAgentResponse(
  userInput: string,
  history: Message[]
): Promise<string> {
  const apiKey = process.env.OPENAI_API_KEY;

  if (!apiKey) {
    throw new Error('OPENAI_API_KEY not found in environment variables');
  }

  const modelName = 'gpt-4.1-nano';

  // Instructions optimisées pour éviter la répétition
  const instructions =
    "Tu es le jumeau virtuel de Rémi, étudiant en Science des Données. " +
    "Sois concis, professionnel et chaleureux. " +
    "Ne te présente pas à chaque phrase si la conversation est déjà engagée. " +
    "Réponds en utilisant le contexte fourni.";

  return runAgent(userInput, instructions, apiKey, modelName, history);
}
