// 📁 src/components/CTASection.jsx
import React from "react";
import { Sparkles } from "lucide-react";

const CTASection = () => {
  return (
    <section className="bg-gradient-to-br from-indigo-600 to-purple-600 py-20 px-6 md:px-20 text-white">
      <div className="max-w-4xl mx-auto text-center">
        <div className="flex justify-center mb-4 animate-bounce">
          <Sparkles className="w-8 h-8 text-yellow-300" />
        </div>
        <h2 className="text-4xl md:text-5xl font-bold leading-tight mb-6 animate-fade-in">
          Ready to unlock smarter shopping with RetailGenie?
        </h2>
        <p className="text-lg md:text-xl mb-10 text-indigo-100">
          AI-powered insights, effortless inventory control, and personalized experiences — all in one platform.
        </p>
        <button className="bg-white text-indigo-700 font-semibold px-8 py-3 rounded-full shadow-lg hover:scale-105 hover:bg-indigo-100 transition transform duration-300">
          Try RetailGenie Now
        </button>
      </div>
    </section>
  );
};

export default CTASection;
