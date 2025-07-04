import React from 'react';
import doodle from '../assets/ai-doodle.png';

const Hero = () => {
  return (
    <section className="min-h-screen flex flex-col-reverse md:flex-row items-center justify-between px-6 md:px-20 pt-24 md:pt-32 bg-indigo-50">
      {/* Text Section */}
      <div className="md:w-1/2 space-y-6 text-center md:text-left">
        <h1 className="text-4xl md:text-5xl font-bold text-indigo-700 leading-tight">
          Your Smart Retail Assistant
        </h1>
        <p className="text-gray-600 text-lg">
          RetailGenie helps you optimize inventory, assist customers, and make smarter decisions — all powered by AI.
        </p>
        <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-full transition font-medium">
          Try RetailGenie
        </button>
      </div>

      {/* Doodle Illustration */}
      <div className="md:w-1/2 flex justify-center md:justify-end mb-8 md:mb-0">
        <img
          src={doodle}
          alt="AI Doodle"
          className="h-72 md:h-96 animate-float"
        />
      </div>
    </section>
  );
};

export default Hero;
