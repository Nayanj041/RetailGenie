import React from "react";

const Navbar = () => {
  return (
    <nav className="flex justify-between items-center px-6 md:px-20 py-4 bg-white shadow">
      <div className="flex items-center gap-2">
        <img src="/src/assets/new retaillogo.png" alt="RetailGenie" className="h-10" />
        <span className="text-lg font-bold text-indigo-700">RetailGenie</span>
      </div>
      <ul className="hidden md:flex gap-8 text-gray-600 font-medium">
        <li className="hover:text-indigo-700 cursor-pointer">Features</li>
        <li className="hover:text-indigo-700 cursor-pointer">Analytics</li>
        <li className="hover:text-indigo-700 cursor-pointer">Pricing</li>
      </ul>
    </nav>
  );
};

export default Navbar;

