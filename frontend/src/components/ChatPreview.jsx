import React from "react";
import { Send } from "lucide-react";

const ChatPreview = () => {
  return (
    <section className="bg-indigo-50 px-6 md:px-20 py-20">
      <div className="max-w-3xl mx-auto bg-white rounded-xl shadow-xl p-6 md:p-10 relative overflow-hidden">
        <h2 className="text-3xl font-bold text-indigo-700 mb-6 text-center">
          Talk to RetailGenie 💬
        </h2>

        {/* Chat area */}
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {/* User Message */}
          <div className="flex justify-end">
            <div className="bg-indigo-100 text-indigo-900 px-4 py-2 rounded-l-xl rounded-br-xl max-w-xs">
              Show me best-selling products this week.
            </div>
          </div>

          {/* Genie AI Message */}
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-800 px-4 py-2 rounded-r-xl rounded-bl-xl max-w-xs">
              Sure! 📈 Here's a quick summary:
              <ul className="list-disc list-inside text-sm mt-1">
                <li>Nike Air Max 2024 - 140 units</li>
                <li>Urban GenZ Hoodie - 103 units</li>
                <li>BlueBerry Organic Face Wash - 90 units</li>
              </ul>
            </div>
          </div>

          {/* Typing animation */}
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-600 px-4 py-2 rounded-r-xl rounded-bl-xl max-w-xs animate-pulse">
              RetailGenie is typing...
            </div>
          </div>
        </div>

        {/* Input area */}
        <div className="flex items-center mt-8 border-t pt-4">
          <input
            type="text"
            placeholder="Type a message..."
            className="flex-grow px-4 py-2 border rounded-l-xl focus:outline-none"
            disabled
          />
          <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-r-xl cursor-not-allowed">
            <Send size={18} />
          </button>
        </div>

        {/* Badge */}
        <span className="absolute top-4 right-4 text-xs text-gray-400">Demo Only</span>
      </div>
    </section>
  );
};

export default ChatPreview;
