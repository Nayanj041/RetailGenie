
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Features from "./components/Features";
import AnalyticsPreview from "./components/AnalyticsPreview";
import ChatPreview from "./components/ChatPreview";
import CTASection from "./components/CTASection";
import Footer from "./components/Footer";


function App() {
  return (
    <div className="bg-gray-100 dark:bg-gray-950 min-h-screen text-black dark:text-white">
      <Navbar />
      <Hero />
      <Features />
      <AnalyticsPreview />
      <ChatPreview />
      <CTASection />
      <Footer />
    </div>
  );
}

export default App;
