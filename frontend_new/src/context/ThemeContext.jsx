import { createContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export function ThemeProvider({ children }) {
  const [isDark, setIsDark] = useState(() => {
    // Check localStorage for saved theme preference
    const saved = localStorage.getItem('theme');
    if (saved) return saved === 'dark';
    // Default to light mode
    return false;
  });

  useEffect(() => {
    // Save theme preference
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    
    // Apply theme to document
    if (isDark) {
      document.documentElement.style.setProperty('--bg-primary', '#1a1a2e');
      document.documentElement.style.setProperty('--bg-secondary', '#16213e');
      document.documentElement.style.setProperty('--text-primary', '#e0e0e0');
      document.documentElement.style.setProperty('--text-secondary', '#b0b0b0');
      document.documentElement.style.setProperty('--navbar-bg', '#0f3460');
      document.documentElement.style.setProperty('--card-bg', '#16213e');
      document.documentElement.style.setProperty('--border-color', '#2c3e50');
    } else {
      document.documentElement.style.setProperty('--bg-primary', '#f5f7fa');
      document.documentElement.style.setProperty('--bg-secondary', '#ffffff');
      document.documentElement.style.setProperty('--text-primary', '#333333');
      document.documentElement.style.setProperty('--text-secondary', '#666666');
      document.documentElement.style.setProperty('--navbar-bg', 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)');
      document.documentElement.style.setProperty('--card-bg', '#f8f9fa');
      document.documentElement.style.setProperty('--border-color', '#e3e6ef');
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
