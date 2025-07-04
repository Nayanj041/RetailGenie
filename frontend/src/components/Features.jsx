import React from "react";
import { ShoppingCart, BarChart, Box, Bot } from "lucide-react";

const features = [
  { icon: <ShoppingCart />, title: "Personalized Shopping", desc: "Track and improve your stores online shopping experience smoothly." },
  { icon: <BarChart />, title: "Store Analytics", desc: "Optimize store metrics with smart AI-powered insights." },
  { icon: <Box />, title: "Inventory Optimization", desc: "Track and optimize store inventory easily." },
  { icon: <Bot />, title: "AI Chat Assistant", desc: "Chat for retail insights at any time." },
];

const Features = () => {
  return (
    <section className="py-20 px-6 md:px-20 bg-white">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-12 text-gray-800">Key Features</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feat, i) => (
            <div key={i} className="p-6 bg-indigo-50 rounded-xl shadow hover:scale-105 transition-all">
              <div className="text-indigo-600 mb-4">{feat.icon}</div>
              <h3 className="font-bold text-lg mb-2">{feat.title}</h3>
              <p className="text-gray-600 text-sm">{feat.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;
