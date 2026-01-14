import React, { useState, useRef, useEffect } from 'react';
import { Send, Database, CheckCircle, Loader, Trash2, Copy } from 'lucide-react';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [schema, setSchema] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  useEffect(() => {
    fetch('http://localhost:5000/api/schema')
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          const formatted = {
            tables: Object.keys(data.schema).map(name => ({
              name,
              columns: data.schema[name].columns
            }))
          };
          setSchema(formatted);
        }
      })
      .catch(err => console.error('Schema fetch failed:', err));
  }, []);

  const handleSubmit = async () => {
    if (!input.trim()) return;

    const userMsg = {
      id: Date.now(),
      type: 'user',
      content: input
    };

    setMessages(prev => [...prev, userMsg]);
    const query = input;
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('http://localhost:5000/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });

      const data = await res.json();

      if (data.success) {
        setMessages(prev => [...prev, {
          id: Date.now(),
          type: 'assistant',
          sql: data.sql,
          explanation: data.explanation,
          results: data.results,
          executionTime: data.execution_time
        }]);
      } else {
        setMessages(prev => [...prev, {
          id: Date.now(),
          type: 'error',
          content: data.error
        }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, {
        id: Date.now(),
        type: 'error',
        content: 'Failed to connect to backend'
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Sidebar */}
      <div className="w-80 bg-slate-800 border-r border-slate-700 p-6 overflow-y-auto">
        <div className="flex items-center gap-3 mb-6">
          <Database className="w-8 h-8 text-blue-400" />
          <h1 className="text-2xl font-bold text-white">SQL Agent</h1>
        </div>

        <div className="mb-6">
          <h2 className="text-sm font-semibold text-slate-400 mb-3 uppercase">Database Schema</h2>
          {schema && schema.tables.map((table, idx) => (
            <div key={idx} className="mb-4 bg-slate-900 rounded-lg p-4 border border-slate-700">
              <h3 className="text-white font-semibold mb-2 flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                {table.name}
              </h3>
              <div className="space-y-1">
                {table.columns.map((col, cidx) => (
                  <div key={cidx} className="text-xs text-slate-400 pl-4">• {col}</div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="p-4 bg-slate-900 rounded-lg border border-slate-700">
          <h3 className="text-sm font-semibold text-slate-400 mb-2">Example Queries</h3>
          <div className="space-y-2 text-xs text-slate-300">
            <div>• Show all customers</div>
            <div>• Which city has most customers?</div>
            <div>• Top 5 expensive products</div>
            <div>• Count products by category</div>
          </div>
        </div>
      </div>

      {/* Main Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-slate-800 border-b border-slate-700 px-6 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-white">Natural Language to SQL</h2>
            <p className="text-sm text-slate-400">Ask questions in plain English</p>
          </div>
          <button
            onClick={() => setMessages([])}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg flex items-center gap-2"
          >
            <Trash2 className="w-4 h-4" />
            Clear
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Database className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-slate-300 mb-2">Start a conversation</h3>
                <p className="text-slate-500">Ask questions about your database</p>
              </div>
            </div>
          )}

          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              {msg.type === 'user' ? (
                <div className="bg-blue-600 text-white rounded-2xl px-6 py-3 max-w-2xl">
                  {msg.content}
                </div>
              ) : msg.type === 'error' ? (
                <div className="bg-red-900 border border-red-700 text-white rounded-2xl px-6 py-3 max-w-2xl">
                  ❌ {msg.content}
                </div>
              ) : (
                <div className="bg-slate-800 rounded-2xl p-6 max-w-4xl w-full border border-slate-700">
                  <div className="mb-4">
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle className="w-5 h-5 text-green-400" />
                      <span className="text-sm font-semibold text-slate-300">Query Generated</span>
                    </div>
                    <p className="text-slate-300">{msg.explanation}</p>
                  </div>

                  <div className="mb-4 bg-slate-900 rounded-lg p-4 border border-slate-700">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-semibold text-slate-400 uppercase">SQL Query</span>
                      <button
                        onClick={() => navigator.clipboard.writeText(msg.sql)}
                        className="text-slate-400 hover:text-white"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                    </div>
                    <code className="text-sm text-blue-300 font-mono">{msg.sql}</code>
                  </div>

                  {msg.results && msg.results.length > 0 && (
                    <div className="bg-slate-900 rounded-lg p-4 border border-slate-700">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-xs font-semibold text-slate-400 uppercase">
                          Results ({msg.results.length} rows)
                        </span>
                        <span className="text-xs text-slate-500">
                          {msg.executionTime.toFixed(2)}ms
                        </span>
                      </div>
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b border-slate-700">
                              {Object.keys(msg.results[0]).map((key, i) => (
                                <th key={i} className="text-left py-2 px-3 text-slate-400 font-semibold">
                                  {key}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {msg.results.map((row, i) => (
                              <tr key={i} className="border-b border-slate-800">
                                {Object.values(row).map((val, j) => (
                                  <td key={j} className="py-2 px-3 text-slate-300">{val}</td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-slate-800 rounded-2xl p-6 border border-slate-700">
                <Loader className="w-5 h-5 text-blue-400 animate-spin" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="bg-slate-800 border-t border-slate-700 p-6">
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about your data..."
              className="flex-1 bg-slate-900 text-white rounded-lg px-4 py-3 border border-slate-700 focus:outline-none focus:border-blue-500"
              disabled={loading}
            />
            <button
              onClick={handleSubmit}
              disabled={loading || !input.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 text-white rounded-lg px-6 py-3 flex items-center gap-2"
            >
              <Send className="w-5 h-5" />
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;