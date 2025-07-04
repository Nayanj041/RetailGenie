// 📁 src/components/Footer.jsx
import React from "react";
import { Mail, MapPin, Instagram, Twitter, Linkedin } from "lucide-react";

const Footer = () => {
  return (
    <footer className="bg-indigo-50 text-gray-800 py-12 px-4 sm:px-6 md:px-20 animate-fade-in-up">
      <div className="max-w-6xl mx-auto grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-10">
        {/* Brand */}
        <div>
          <div className="flex items-center gap-2 mb-4">
            <img src="/src/assets/retaillogo.png" alt="RetailGenie" className="h-10 w-auto" />
            <h2 className="text-xl font-bold text-indigo-700">RetailGenie</h2>
          </div>
          <p className="text-sm text-gray-600">
            Your AI-powered retail assistant for smarter shopping, inventory & insights.
          </p>
        </div>

        {/* Quick Links */}
        <div>
          <h3 className="text-indigo-800 font-semibold mb-3">Quick Links</h3>
          <ul className="space-y-2 text-sm">
            <li className="hover:text-indigo-600 hover:underline cursor-pointer transition duration-200">Home</li>
            <li className="hover:text-indigo-600 hover:underline cursor-pointer transition duration-200">Features</li>
            <li className="hover:text-indigo-600 hover:underline cursor-pointer transition duration-200">Analytics</li>
            <li className="hover:text-indigo-600 hover:underline cursor-pointer transition duration-200">Contact</li>
          </ul>
        </div>

        {/* Contact Info */}
        <div>
          <h3 className="text-indigo-800 font-semibold mb-3">Contact Us</h3>
          <ul className="space-y-2 text-sm">
            <li className="flex items-center gap-2">
              <Mail size={16} className="text-indigo-600" /> support@retailgenie.ai
            </li>
            <li className="flex items-center gap-2">
              <MapPin size={16} className="text-indigo-600" /> Pune, India
            </li>
          </ul>
        </div>

        {/* Social Media */}
        <div>
          <h3 className="text-indigo-800 font-semibold mb-3">Follow Us</h3>
          <div className="flex gap-4 text-indigo-500">
            <Instagram aria-label="Instagram" className="hover:text-pink-500 transition transform hover:scale-110 cursor-pointer" />
            <Twitter aria-label="Twitter" className="hover:text-blue-500 transition transform hover:scale-110 cursor-pointer" />
            <Linkedin aria-label="LinkedIn" className="hover:text-blue-700 transition transform hover:scale-110 cursor-pointer" />
          </div>
        </div>
      </div>

      <div className="text-center text-xs text-gray-500 mt-12">
        © 2025 RetailGenie. All rights reserved.
      </div>
    </footer>
  );
};

export default Footer;
