// 📁 src/components/Features.jsx
import React from "react";
import { Zap, Layers, Eye, BarChart3 } from "lucide-react";

const features = [
  {
    icon: <Zap className="w-8 h-8 text-indigo-600" />,
    title: "Smart AI Assistant",
    desc: "Personalized recommendations using customer behavior analysis.",
  },
  {
    icon: <Layers className="w-8 h-8 text-indigo-600" />,
    title: "Inventory Optimization",
    desc: "Track, forecast, and manage inventory in real-time.",
  },
  {
    icon: <BarChart3 className="w-8 h-8 text-indigo-600" />,
    title: "Sales Analytics",
    desc: "Understand what sells, when, and why with beautiful insights.",
  },
  {
    icon: <Eye className="w-8 h-8 text-indigo-600" />,
    title: "Customer Insights",
    desc: "Get to know your customers’ preferences and buying patterns.",
  },
];

const Features = () => {
  return (
    <section className="bg-white py-20 px-4 sm:px-6 md:px-20">
      <div className="max-w-6xl mx-auto text-center">
        <h2 className="text-3xl sm:text-4xl font-bold text-gray-800 mb-12 animate-fade-in">
          Powerful Features to Elevate Your Store
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-indigo-50 rounded-xl p-6 text-left shadow-md hover:shadow-xl transition duration-300 transform hover:-translate-y-1"
            >
              {feature.icon}
              <h3 className="text-xl font-semibold mt-4 mb-2 text-indigo-800">
                {feature.title}
              </h3>
              <p className="text-gray-600 text-sm">{feature.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;
