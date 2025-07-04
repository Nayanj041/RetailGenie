import React from "react";
import { Sparkles, PackageSearch, BarChart3, MessageSquare } from "lucide-react";

const features = [
  {
    icon: <Sparkles className="h-8 w-8 text-indigo-600" />,
    title: "Personalized Shopping Assistant",
    desc: "Recommends products tailored to customer behavior, past purchases, and preferences.",
  },
  {
    icon: <PackageSearch className="h-8 w-8 text-indigo-600" />,
    title: "AI-Based Inventory Forecasting",
    desc: "Predicts inventory needs using trends and demand, helping avoid overstock or shortage.",
  },
  {
    icon: <BarChart3 className="h-8 w-8 text-indigo-600" />,
    title: "Store Analytics Dashboard",
    desc: "Visualizes sales trends, customer flow, and product performance across stores.",
  },
  {
    icon: <MessageSquare className="h-8 w-8 text-indigo-600" />,
    title: "RetailGenie Chat Interface",
    desc: "Your 24/7 AI assistant for staff queries, store insights, and task automation.",
  },
];

const Features = () => {
  return (
    <section className="py-20 bg-white px-6 md:px-20">
      <div className="text-center mb-12">
        <h2 className="text-4xl font-bold text-indigo-700">What RetailGenie Can Do</h2>
        <p className="text-gray-500 mt-2">
          Meet your AI-powered assistant — smart, scalable, and made for modern retail.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-8">
        {features.map((item, index) => (
          <div
            key={index}
            className="p-6 bg-indigo-50 hover:bg-indigo-100 rounded-xl shadow-md hover:shadow-xl transform transition hover:-translate-y-2"
          >
            {item.icon}
            <h3 className="text-xl font-semibold mt-4 text-indigo-800">
              {item.title}
            </h3>
            <p className="mt-2 text-gray-600">{item.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
};

export default Features;
