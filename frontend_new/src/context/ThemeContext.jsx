import { createContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export function ThemeProvider({ children }) {
  const [isDark, setIsDark] = useState(() => {
    // Check localStorage for saved theme preference
    const saved = localStorage.getItem('theme');
    if (saved) return saved === 'dark';
    // Default to DARK mode
    return true;
  });

  useEffect(() => {
    // Save theme preference
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    
    // Apply theme to document
    if (isDark) {
      // DARK MODE - Improved contrast and readability
      document.documentElement.style.setProperty('--bg-primary', '#1a1a2e');
      document.documentElement.style.setProperty('--bg-secondary', '#16213e');
      document.documentElement.style.setProperty('--text-primary', '#ffffff');      // Pure white for primary text
      document.documentElement.style.setProperty('--text-secondary', '#d0d0d0');    // Light grey for secondary text
      document.documentElement.style.setProperty('--navbar-bg', '#0f3460');
      document.documentElement.style.setProperty('--card-bg', '#16213e');
      document.documentElement.style.setProperty('--card-container-bg', '#0f1b2e'); // Dark blue containers
      document.documentElement.style.setProperty('--card-border', '#2c3e50');       // Dark borders
      document.documentElement.style.setProperty('--card-shadow', '0 2px 8px rgba(0, 0, 0, 0.3)'); // Darker shadow
      document.documentElement.style.setProperty('--border-color', '#2c3e50');
      document.documentElement.style.setProperty('--text-muted', '#a0a0a0');       // Medium grey for muted text
      document.documentElement.style.setProperty('--text-light-grey', '#c0c0c0');  // Lighter grey for labels
    } else {
      // LIGHT MODE - Original design
      document.documentElement.style.setProperty('--bg-primary', '#f5f7fa');
      document.documentElement.style.setProperty('--bg-secondary', '#ffffff');
      document.documentElement.style.setProperty('--text-primary', '#333333');
      document.documentElement.style.setProperty('--text-secondary', '#666666');
      document.documentElement.style.setProperty('--navbar-bg', 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)');
      document.documentElement.style.setProperty('--card-bg', '#f8f9fa');
      document.documentElement.style.setProperty('--card-container-bg', '#ffffff'); // White containers
      document.documentElement.style.setProperty('--card-border', '#e0e0e0');      // Light borders
      document.documentElement.style.setProperty('--card-shadow', '0 2px 8px rgba(0, 0, 0, 0.1)'); // Light shadow
      document.documentElement.style.setProperty('--border-color', '#e3e6ef');
      document.documentElement.style.setProperty('--text-muted', '#999999');
      document.documentElement.style.setProperty('--text-light-grey', '#666666');
    }
  }, [isDark]);

  const toggleTheme = () => {
    setIsDark(!isDark);
  };

  return (
    <ThemeContext.Provider value={{ isDark, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export default ThemeContext;
