// 📁 src/components/ChatPreview.jsx
import React from "react";

const ChatPreview = () => {
  return (
    <section className="bg-white py-20 px-4 sm:px-6 md:px-20">
      <div className="max-w-4xl mx-auto text-center">
        <h2 className="text-3xl sm:text-4xl font-bold text-gray-800 mb-8 animate-fade-in">
          Meet Your Genie: Smart Shopping Chat
        </h2>

        {/* Chat Window Preview */}
        <div className="bg-indigo-50 rounded-xl p-6 shadow-xl max-w-xl mx-auto text-left space-y-4 animate-fade-in-up">
          
          {/* Assistant Message */}
          <div className="flex items-start gap-3">
            <img
              src="/src/assets/retaillogo.png"
              alt="Genie"
              className="h-10 w-10 rounded-full"
            />
            <div className="bg-white px-4 py-3 rounded-lg shadow text-sm text-gray-700 max-w-[80%]">
              Hello! I’m RetailGenie 🤖. Looking for something specific today?
            </div>
          </div>

          {/* User Message */}
          <div className="flex items-start justify-end gap-3">
            <div className="bg-indigo-600 text-white px-4 py-3 rounded-lg shadow text-sm max-w-[80%]">
              I need a suggestion for trending fitness shoes!
            </div>
            <img
              src="https://api.dicebear.com/6.x/thumbs/svg?seed=user"
              alt="User"
              className="h-10 w-10 rounded-full"
            />
          </div>

          {/* Assistant Reply */}
          <div className="flex items-start gap-3">
            <img
              src="/src/assets/retaillogo.png"
              alt="Genie"
              className="h-10 w-10 rounded-full"
            />
            <div className="bg-white px-4 py-3 rounded-lg shadow text-sm text-gray-700 max-w-[80%]">
              Great choice! Here's a list of top-rated shoes in your size 🏃‍♀️✨
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ChatPreview;
