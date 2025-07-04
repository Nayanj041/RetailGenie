// 📁 src/components/Analytics.jsx
import React from "react";
import { TrendingUp, Users, PackageCheck, Wallet } from "lucide-react";

const stats = [
  {
    icon: <TrendingUp className="w-8 h-8 text-indigo-600" />,
    label: "Total Revenue",
    value: "₹7.5 Cr",
  },
  {
    icon: <Users className="w-8 h-8 text-indigo-600" />,
    label: "Active Customers",
    value: "24.3K",
  },
  {
    icon: <PackageCheck className="w-8 h-8 text-indigo-600" />,
    label: "Orders Fulfilled",
    value: "56.8K",
  },
  {
    icon: <Wallet className="w-8 h-8 text-indigo-600" />,
    label: "Avg. Order Value",
    value: "₹1,320",
  },
];

const Analytics = () => {
  return (
    <section className="bg-indigo-50 py-20 px-4 sm:px-6 md:px-20">
      <div className="max-w-6xl mx-auto text-center">
        <h2 className="text-3xl sm:text-4xl font-bold text-gray-800 mb-12 animate-fade-in">
          Store Insights At a Glance
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {stats.map((item, index) => (
            <div
              key={index}
              className="bg-white rounded-xl p-6 shadow hover:shadow-lg transition transform hover:-translate-y-1"
            >
              {item.icon}
              <h3 className="text-xl font-semibold mt-4 mb-2 text-indigo-700">{item.value}</h3>
              <p className="text-sm text-gray-600">{item.label}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Analytics;
