
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Features from "./components/Features";
import AnalyticsPreview from "./components/AnalyticsPreview";

function App() {
  return (
    <div className="bg-gray-100 dark:bg-gray-950 min-h-screen text-black dark:text-white">
      <Navbar />
      <Hero />
      <Features />
      <AnalyticsPreview />
    </div>
  );
}

export default App;
