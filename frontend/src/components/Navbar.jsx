// 📁 src/components/Navbar.jsx
import React, { useState } from "react";
import ThemeToggle from "./ThemeToggle";
import { Menu, X } from "lucide-react";

const Navbar = () => {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <nav className="bg-white shadow-md sticky top-0 z-50 px-4 sm:px-6 md:px-20 py-4 transition-all">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <img src="/src/assets/retaillogo.png" alt="RetailGenie" className="h-10 w-auto" />
          <span className="text-xl font-bold text-indigo-700">RetailGenie</span>
        </div>

        {/* Desktop Menu */}
        <ul className="hidden md:flex gap-10 text-gray-700 font-medium">
          <li className="hover:text-indigo-700 hover:scale-105 transition cursor-pointer">Features</li>
          <li className="hover:text-indigo-700 hover:scale-105 transition cursor-pointer">Analytics</li>
          <li className="hover:text-indigo-700 hover:scale-105 transition cursor-pointer">Pricing</li>
        </ul>

        {/* Right Side */}
        <div className="flex items-center gap-4">
          <ThemeToggle />
          {/* Hamburger for Mobile */}
          <button
            className="md:hidden p-2 rounded hover:bg-indigo-100 transition"
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="Toggle menu"
          >
            {menuOpen ? <X /> : <Menu />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {menuOpen && (
        <div className="md:hidden mt-4 px-2 animate-fade-in">
          <ul className="flex flex-col gap-4 text-gray-700 font-medium">
            <li className="hover:text-indigo-700 hover:scale-105 transition cursor-pointer">Features</li>
            <li className="hover:text-indigo-700 hover:scale-105 transition cursor-pointer">Analytics</li>
            <li className="hover:text-indigo-700 hover:scale-105 transition cursor-pointer">Pricing</li>
          </ul>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
