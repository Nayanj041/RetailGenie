import React from "react";
import { Send } from "lucide-react";

const ChatPreview = () => {
  return (
    <section className="bg-white px-6 md:px-20 py-20">
      <div className="max-w-3xl mx-auto bg-indigo-50 rounded-xl shadow-xl p-6 md:p-10">
        <h2 className="text-3xl font-bold text-indigo-700 mb-6 text-center">
          AI Chat Assistant
        </h2>

        <div className="space-y-4 max-h-96 overflow-y-auto">
          <div className="flex justify-end">
            <div className="bg-indigo-100 text-indigo-900 px-4 py-2 rounded-l-xl rounded-br-xl max-w-xs">
              Can you recommend a product for summer?
            </div>
          </div>

          <div className="flex justify-start">
            <div className="bg-white text-gray-800 px-4 py-2 rounded-r-xl rounded-bl-xl max-w-xs shadow">
              Of course! I suggest our lightweight summer dresses for your needs.
            </div>
          </div>
        </div>

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
      </div>
    </section>
  );
};

export default ChatPreview;
