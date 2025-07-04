// 📁 src/components/Hero.jsx
import React from "react";

const Hero = () => {
  return (
    <section className="bg-indigo-50 py-16 px-4 sm:px-6 md:px-20">
      <div className="max-w-6xl mx-auto flex flex-col-reverse md:flex-row items-center gap-12">
        
        {/* Text Content */}
        <div className="flex-1 text-center md:text-left">
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-gray-800 leading-tight animate-fade-in">
            AI-powered smart assistant <br /> for personalized shopping
          </h1>
          <p className="text-gray-600 mt-4 text-base sm:text-lg md:text-xl">
            Enhance your retail experience with AI-driven recommendations, analytics & inventory magic.
          </p>
          <button className="mt-6 bg-indigo-600 text-white px-6 py-3 rounded-xl hover:bg-indigo-700 hover:scale-105 transition duration-300 shadow-lg">
            Get Started
          </button>
        </div>

        {/* Image / Illustration */}
        <div className="flex-1">
          <img
            src="/src/assets/retaillogo.png"
            alt="RetailGenie"
            className="w-full max-w-xs sm:max-w-sm md:max-w-md mx-auto animate-fade-in-up"
          />
        </div>
      </div>
    </section>
  );
};

export default Hero;
