import { BarChart3, AlertTriangle, UsersRound, Boxes } from "lucide-react";

function AnalyticsPreview() {
  const insights = [
    {
      icon: <Boxes className="w-8 h-8 text-indigo-600" />,
      title: "Inventory Optimization",
      desc: "Track stock in real-time and avoid over/under stocking.",
    },
    {
      icon: <BarChart3 className="w-8 h-8 text-green-600" />,
      title: "Sales Forecasting",
      desc: "Predict demand trends to boost revenue and efficiency.",
    },
    {
      icon: <UsersRound className="w-8 h-8 text-yellow-500" />,
      title: "Customer Behavior",
      desc: "Understand shopper patterns and personalize offers.",
    },
    {
      icon: <AlertTriangle className="w-8 h-8 text-red-500" />,
      title: "Smart Alerts",
      desc: "Receive low-stock or high-demand notifications instantly.",
    },
  ];

  return (
    <section className="py-20 px-6 bg-gray-50 dark:bg-gray-900">
      <h2 className="text-4xl font-bold text-center mb-12 text-indigo-700">
        Real-Time Retail Analytics
      </h2>
      <div className="flex flex-col lg:flex-row items-center gap-12">
        {/* Placeholder Image (replace with dashboard screenshot later) */}
        <div className="flex-1">
          <img
            src="/dashboard-mock.png"
            alt="Dashboard Preview"
            className="w-full rounded-xl shadow-lg"
          />
        </div>

        {/* Insights List */}
        <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-6">
          {insights.map((item, index) => (
            <div
              key={index}
              className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow hover:shadow-xl transition"
            >
              <div className="mb-3">{item.icon}</div>
              <h3 className="text-xl font-semibold mb-1">{item.title}</h3>
              <p className="text-gray-600 dark:text-gray-300">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default AnalyticsPreview;
