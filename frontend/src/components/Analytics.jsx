import React from "react";

const Analytics = () => {
  return (
    <section className="py-20 px-6 md:px-20 bg-indigo-50">
      <div className="max-w-5xl mx-auto">
        <h2 className="text-3xl font-bold text-gray-800 mb-10 text-center">
          Store Insights & Analytics
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white p-6 rounded-xl shadow text-center">
            <h3 className="text-indigo-600 font-semibold">$15.2K</h3>
            <p className="text-sm text-gray-500">Revenue</p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow text-center">
            <h3 className="text-indigo-600 font-semibold">1.2K</h3>
            <p className="text-sm text-gray-500">Orders</p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow text-center">
            <h3 className="text-indigo-600 font-semibold">1.3K</h3>
            <p className="text-sm text-gray-500">Customers</p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow text-center">
            <img src="/src/assets/chart-mock.png" alt="chart" className="h-32 mx-auto" />
          </div>
        </div>
      </div>
    </section>
  );
};

export default Analytics;
