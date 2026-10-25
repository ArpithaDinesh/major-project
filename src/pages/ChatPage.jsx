import React, { useState, useRef, useEffect } from 'react';
import { 
  Bot, 
  Send, 
  Sparkles, 
  Trash2, 
  Loader2, 
  Compass 
} from 'lucide-react';
import { knowledgeApi } from '../services/api';
import { ChatBubble } from '../components/chat/ChatBubble';
import { MemoraLogo } from '../components/common/MemoraLogo';
import { MOCK_CHAT_SUGGESTIONS } from '../services/mockData';

export const ChatPage = () => {
  const [messages, setMessages] = useState([
    {
      id: 'welcome-1',
      sender: 'assistant',
      text: "Hello! I am your **Memora assistant**. I have indexed all your personal notes, voice recordings, diagrams, PDFs, and web bookmarks into memory.\n\nAsk me anything like *'When is my next deadline?'* or *'What did we discuss in the mobile sync voice memo?'*",
      sources: []
    }
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (queryToSend) => {
    const query = (queryToSend || inputQuery).trim();
    if (!query || isLoading) return;

    setInputQuery('');

    // Append user message
    const userMsg = {
      id: `usr-${Date.now()}`,
      sender: 'user',
      text: query,
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      // Query Assistant API
      const response = await knowledgeApi.queryChat(query, messages);

      const assistantMsg = {
        id: `ast-${Date.now()}`,
        sender: 'assistant',
        text: response.reply,
        sources: response.sources || []
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      const errorMsg = {
        id: `err-${Date.now()}`,
        sender: 'assistant',
        text: "I encountered an error querying your knowledge base. Please check your connection or try rephrasing your question.",
        sources: []
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearHistory = () => {
    setMessages([
      {
        id: `welcome-${Date.now()}`,
        sender: 'assistant',
        text: "Conversation cleared. How can I help you query your personal knowledge repository?",
        sources: []
      }
    ]);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8.5rem)] md:h-[calc(100vh-6.5rem)] pb-4 max-w-4xl mx-auto">
      {/* Top Chat Bar (Context Active button, RAG, and subtitle removed) */}
      <div className="flex items-center justify-between pb-4 border-b border-dark-border/80 shrink-0">
        <div className="flex items-center gap-3">
          <MemoraLogo size="md" />
          <h1 className="text-base font-bold text-palette-navy dark:text-white">
            Memora Assistant
          </h1>
        </div>

        <button
          onClick={handleClearHistory}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-palette-border dark:border-dark-border hover:bg-palette-cream dark:hover:bg-dark-hover text-palette-slate dark:text-app-subtle hover:text-palette-navy dark:hover:text-white text-xs font-medium transition-colors cursor-pointer"
          title="Clear chat history"
        >
          <Trash2 className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Clear Chat</span>
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto py-6 space-y-6 pr-2">
        {messages.map((msg) => (
          <ChatBubble key={msg.id} message={msg} />
        ))}

        {isLoading && (
          <div className="flex items-start gap-3 max-w-xl mr-auto animate-fadeIn">
            <div className="w-8 h-8 rounded-xl bg-accent/20 border border-accent/40 flex items-center justify-center text-accent-light shrink-0">
              <Sparkles className="w-4 h-4 animate-spin text-accent-light" />
            </div>
            <div className="bg-dark-card border border-dark-border rounded-2xl rounded-tl-sm p-4 text-xs text-app-muted flex items-center gap-2.5">
              <Loader2 className="w-4 h-4 animate-spin text-accent-light" />
              <span>Searching knowledge base and generating answer...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Queries Chips */}
      {messages.length <= 3 && (
        <div className="pb-3 shrink-0">
          <div className="flex items-center gap-1.5 text-[11px] font-semibold text-app-subtle uppercase tracking-wider mb-2">
            <Compass className="w-3.5 h-3.5 text-accent-light" />
            <span>Suggested Inquiries</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {MOCK_CHAT_SUGGESTIONS.map((suggestion, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(suggestion)}
                className="text-xs px-3 py-1.5 rounded-xl bg-white dark:bg-dark-surface hover:bg-palette-cream dark:hover:bg-dark-hover border border-palette-border dark:border-dark-border hover:border-palette-slate text-palette-slate dark:text-app-muted hover:text-palette-navy dark:hover:text-white transition-all text-left cursor-pointer truncate max-w-full"
              >
                "{suggestion}"
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Chat Input Container (Disclaimer copy removed) */}
      <div className="shrink-0 pt-2">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="relative flex items-center"
        >
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            disabled={isLoading}
            placeholder="Ask a question about your notes, voice memos, diagrams, or documents..."
            className="w-full bg-white dark:bg-dark-surface/90 border border-palette-border dark:border-dark-border focus:border-palette-navy dark:focus:border-accent/70 rounded-2xl pl-4 pr-24 py-3.5 text-sm text-palette-navy dark:text-white placeholder-palette-slate/60 dark:placeholder-app-subtle transition-all outline-none shadow-soft-card"
          />
          <button
            type="submit"
            disabled={isLoading || !inputQuery.trim()}
            className="absolute right-2 px-4 py-2 rounded-xl bg-palette-navy hover:bg-palette-slate text-white text-xs font-semibold disabled:opacity-40 transition-all flex items-center gap-1.5 cursor-pointer shadow-sm"
          >
            <span>Ask</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>
    </div>
  );
};
