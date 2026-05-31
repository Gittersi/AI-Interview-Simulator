import { create } from 'zustand';

export const useAuthStore = create((set) => ({
  user: null,
  token: localStorage.getItem('authToken'),
  setUser: (user) => set({ user }),
  setToken: (token) => {
    if (token) {
      localStorage.setItem('authToken', token);
    } else {
      localStorage.removeItem('authToken');
    }
    set({ token });
  },
  logout: () => {
    localStorage.removeItem('authToken');
    set({ user: null, token: null });
  },
}));

export const useInterviewStore = create((set) => ({
  currentInterview: null,
  currentQuestion: null,
  setCurrentInterview: (interview) => set({ currentInterview: interview }),
  setCurrentQuestion: (question) => set({ currentQuestion: question }),
}));

export const useThemeStore = create((set) => {
  const saved = localStorage.getItem('theme') || 'light';
  const isDark = saved === 'dark';
  if (isDark) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }

  return {
    isDarkMode: isDark,
    toggleDarkMode: () => {
      set((state) => {
        const newIsDark = !state.isDarkMode;
        localStorage.setItem('theme', newIsDark ? 'dark' : 'light');
        if (newIsDark) {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }
        return { isDarkMode: newIsDark };
      });
    },
    setDarkMode: (isDark) => {
      localStorage.setItem('theme', isDark ? 'dark' : 'light');
      if (isDark) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
      set({ isDarkMode: isDark });
    },
  };
});
