import React, { useState, useEffect, useRef } from "react";
import {
  Send,
  Mic,
  MicOff,
  Bot,
  User,
  Lightbulb,
  TrendingUp,
  Package,
  DollarSign,
} from "lucide-react";
import LoadingSpinner from "../components/LoadingSpinner";
import { useAuth } from "../utils/AuthContext";
import { api } from "../utils/api";

const AIAssistant = () => {
  const { token } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const messagesEndRef = useRef(null);
  const recognition = useRef(null);

  const quickActions = [
    {
      icon: TrendingUp,
      title: "Sales Analytics",
      description: "Show me today's sales performance",
      query:
        "What are today's sales metrics and how do they compare to yesterday?",
    },
    {
      icon: Package,
      title: "Inventory Status",
      description: "Check low stock items",
      query: "Which products are running low on inventory and need restocking?",
    },
    {
      icon: DollarSign,
      title: "Revenue Insights",
      description: "Analyze revenue trends",
      query:
        "Analyze our revenue trends for the past week and provide insights",
    },
    {
      icon: Lightbulb,
      title: "Product Recommendations",
      description: "Get AI-powered suggestions",
      query:
        "What products should I promote this week based on current trends?",
    },
  ];

  useEffect(() => {
    scrollToBottom();
    fetchChatHistory();
    setupSpeechRecognition();

    // Welcome message
    if (messages.length === 0) {
      setMessages([
        {
          id: 1,
          content:
            "Hello! I'm your AI retail assistant. I can help you with sales analytics, inventory management, customer insights, and business recommendations. How can I assist you today?",
          sender: "ai",
          timestamp: new Date().toISOString(),
        },
      ]);
    }
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchChatHistory = async () => {
    try {
      const response = await api.get("/ai/chat/history", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.data.messages && response.data.messages.length > 0) {
        setMessages(response.data.messages);
      }
    } catch (error) {
      console.error("Error fetching chat history:", error);
    }
  };

  const setupSpeechRecognition = () => {
    if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
      const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;
      recognition.current = new SpeechRecognition();
      recognition.current.continuous = false;
      recognition.current.interimResults = false;
      recognition.current.lang = "en-US";

      recognition.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputMessage(transcript);
        setIsListening(false);
      };

      recognition.current.onerror = () => {
        setIsListening(false);
      };

      recognition.current.onend = () => {
        setIsListening(false);
      };
    }
  };

  const startListening = () => {
    if (recognition.current) {
      setIsListening(true);
      recognition.current.start();
    }
  };

  const stopListening = () => {
    if (recognition.current) {
      setIsListening(false);
      recognition.current.stop();
    }
  };

  const sendMessage = async (messageText = inputMessage) => {
    if (!messageText.trim()) return;

    const userMessage = {
      id: Date.now(),
      content: messageText,
      sender: "user",
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setLoading(true);

    try {
      const response = await api.post(
        "/ai/chat",
        {
          message: messageText,
          context: "retail_assistant",
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        },
      );

      const aiMessage = {
        id: Date.now() + 1,
        content:
          response.data.response ||
          "I apologize, but I encountered an issue processing your request. Please try again.",
        sender: "ai",
        timestamp: new Date().toISOString(),
        suggestions: response.data.suggestions || [],
      };

      setMessages((prev) => [...prev, aiMessage]);
      setSuggestions(response.data.suggestions || []);
    } catch (error) {
      console.error("Error sending message:", error);

      // Fallback AI response
      const fallbackMessage = {
        id: Date.now() + 1,
        content:
          "I'm currently experiencing some connectivity issues. Here are some things I can help you with:\n\n• Sales analytics and performance metrics\n• Inventory management and restocking alerts\n• Customer feedback analysis\n• Product recommendations\n• Revenue optimization strategies\n\nPlease try your question again, or select one of the quick actions below.",
        sender: "ai",
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, fallbackMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatMessage = (content) => {
    // Simple markdown-like formatting
    return content
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.*?)\*/g, "<em>$1</em>")
      .replace(/\n/g, "<br/>");
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <div className="flex-1 max-w-4xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            AI Assistant
          </h1>
          <p className="text-gray-600">
            Your intelligent retail companion powered by advanced AI
          </p>
        </div>

        {/* Quick Actions */}
        {messages.length <= 1 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            {quickActions.map((action, index) => {
              const Icon = action.icon;
              return (
                <button
                  key={index}
                  onClick={() => sendMessage(action.query)}
                  className="p-4 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow text-left"
                >
                  <div className="flex items-start space-x-3">
                    <div className="bg-blue-100 p-2 rounded-lg">
                      <Icon className="h-6 w-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">
                        {action.title}
                      </h3>
                      <p className="text-sm text-gray-600 mt-1">
                        {action.description}
                      </p>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        )}

        {/* Chat Messages */}
        <div className="bg-white rounded-lg shadow-md flex flex-col h-96 mb-4">
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`flex max-w-xs lg:max-w-md ${message.sender === "user" ? "flex-row-reverse" : "flex-row"}`}
                >
                  <div
                    className={`flex-shrink-0 ${message.sender === "user" ? "ml-3" : "mr-3"}`}
                  >
                    <div
                      className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        message.sender === "user"
                          ? "bg-blue-600"
                          : "bg-gray-600"
                      }`}
                    >
                      {message.sender === "user" ? (
                        <User className="h-5 w-5 text-white" />
                      ) : (
                        <Bot className="h-5 w-5 text-white" />
                      )}
                    </div>
                  </div>
                  <div
                    className={`px-4 py-2 rounded-lg ${
                      message.sender === "user"
                        ? "bg-blue-600 text-white"
                        : "bg-gray-100 text-gray-900"
                    }`}
                  >
                    <div
                      dangerouslySetInnerHTML={{
                        __html: formatMessage(message.content),
                      }}
                    />
                    <div
                      className={`text-xs mt-1 ${
                        message.sender === "user"
                          ? "text-blue-100"
                          : "text-gray-500"
                      }`}
                    >
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="flex mr-3">
                  <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                    <Bot className="h-5 w-5 text-white" />
                  </div>
                </div>
                <div className="bg-gray-100 px-4 py-2 rounded-lg">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: "0.1s" }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: "0.2s" }}
                    ></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Suggestions */}
          {suggestions.length > 0 && (
            <div className="border-t border-gray-200 p-4">
              <p className="text-sm text-gray-600 mb-2">Suggestions:</p>
              <div className="flex flex-wrap gap-2">
                {suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => sendMessage(suggestion)}
                    className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input Area */}
          <div className="border-t border-gray-200 p-4">
            <div className="flex space-x-2">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything about your business..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows="1"
                style={{ minHeight: "40px", maxHeight: "120px" }}
              />

              {/* Voice Input Button */}
              <button
                onClick={isListening ? stopListening : startListening}
                className={`px-3 py-2 rounded-lg transition-colors ${
                  isListening
                    ? "bg-red-600 text-white hover:bg-red-700"
                    : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                }`}
              >
                {isListening ? (
                  <MicOff className="h-5 w-5" />
                ) : (
                  <Mic className="h-5 w-5" />
                )}
              </button>

              {/* Send Button */}
              <button
                onClick={() => sendMessage()}
                disabled={!inputMessage.trim() || loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                <Send className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>

        {/* AI Capabilities */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            What I can help you with:
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="flex items-start space-x-3">
              <TrendingUp className="h-5 w-5 text-blue-600 mt-1" />
              <div>
                <h4 className="font-medium text-gray-900">Sales Analytics</h4>
                <p className="text-sm text-gray-600">
                  Performance metrics, trends, and forecasting
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <Package className="h-5 w-5 text-green-600 mt-1" />
              <div>
                <h4 className="font-medium text-gray-900">
                  Inventory Management
                </h4>
                <p className="text-sm text-gray-600">
                  Stock levels, reorder alerts, and optimization
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <DollarSign className="h-5 w-5 text-purple-600 mt-1" />
              <div>
                <h4 className="font-medium text-gray-900">Pricing Strategy</h4>
                <p className="text-sm text-gray-600">
                  Dynamic pricing and profit optimization
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <User className="h-5 w-5 text-red-600 mt-1" />
              <div>
                <h4 className="font-medium text-gray-900">Customer Insights</h4>
                <p className="text-sm text-gray-600">
                  Behavior analysis and segmentation
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <Lightbulb className="h-5 w-5 text-yellow-600 mt-1" />
              <div>
                <h4 className="font-medium text-gray-900">Recommendations</h4>
                <p className="text-sm text-gray-600">
                  Product suggestions and business strategies
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <Bot className="h-5 w-5 text-indigo-600 mt-1" />
              <div>
                <h4 className="font-medium text-gray-900">Automated Reports</h4>
                <p className="text-sm text-gray-600">
                  Generate insights and summaries instantly
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIAssistant;
