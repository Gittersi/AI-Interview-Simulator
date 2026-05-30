import { create } from 'zustand';
import { User, Interview, Question } from '../types';

interface AuthStore {
  user: User | null;
  token: string | null;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  logout: () => void;
}

interface InterviewStore {
  currentInterview: Interview | null;
  currentQuestion: Question | null;
  setCurrentInterview: (interview: Interview | null) => void;
  setCurrentQuestion: (question: Question | null) => void;
}

interface ThemeStore {
  isDarkMode: boolean;
  toggleDarkMode: () => void;
  setDarkMode: (isDark: boolean) => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
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

export const useInterviewStore = create<InterviewStore>((set) => ({
  currentInterview: null,
  currentQuestion: null,
  setCurrentInterview: (interview) => set({ currentInterview: interview }),
  setCurrentQuestion: (question) => set({ currentQuestion: question }),
}));

export const useThemeStore = create<ThemeStore>((set) => {
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
    setDarkMode: (isDark: boolean) => {
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
