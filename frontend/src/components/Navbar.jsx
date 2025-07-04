import React, { useState } from 'react';
import { Menu, X } from 'lucide-react';
import logo from '../assets/retailgenie-logo.png';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const toggleMenu = () => setIsOpen(!isOpen);

  const navLinks = ['Home', 'Features', 'Dashboard', 'Contact'];

  return (
    <nav className="bg-white shadow-md fixed w-full z-50">
      <div className="flex items-center justify-between px-6 md:px-20 py-4">
        {/* Logo */}
        <div className="flex items-center space-x-2">
          <img src={logo} alt="RetailGenie Logo" className="h-10 w-10" />
          <span className="text-xl font-bold text-indigo-700">RetailGenie</span>
        </div>

        {/* Desktop Menu */}
        <ul className="hidden md:flex space-x-6 text-gray-700 font-medium">
          {navLinks.map((link) => (
            <li key={link} className="hover:text-indigo-600 cursor-pointer transition">
              {link}
            </li>
          ))}
        </ul>

        {/* Mobile Menu Toggle */}
        <div className="md:hidden">
          {isOpen ? (
            <X className="h-6 w-6" onClick={toggleMenu} />
          ) : (
            <Menu className="h-6 w-6" onClick={toggleMenu} />
          )}
        </div>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <ul className="md:hidden px-6 pb-4 bg-white space-y-2 text-gray-700 font-medium transition">
          {navLinks.map((link) => (
            <li key={link} className="hover:text-indigo-600 cursor-pointer">
              {link}
            </li>
          ))}
        </ul>
      )}
    </nav>
  );
};

export default Navbar;
