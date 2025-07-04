import React from "react";

const Hero = () => {
  return (
    <section className="bg-indigo-50 py-16 px-6 md:px-20">
      <div className="max-w-5xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8">
        <div className="flex-1">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-800 leading-tight">
            AI-powered smart assistant for <br /> personalized shopping
          </h1>
          <p className="text-gray-600 mt-4 text-lg">
            Enhance your shopping experience with advanced AI insights and
            recommendations tailored just for you.
          </p>
          <button className="mt-6 bg-indigo-600 text-white px-6 py-3 rounded-xl hover:bg-indigo-700">
            Get Started
          </button>
        </div>
        <img src="/src/assets/new retaillogo.png" className="h-48 md:h-64" alt="RetailGenie Genie" />
      </div>
    </section>
  );
};

export default Hero;
