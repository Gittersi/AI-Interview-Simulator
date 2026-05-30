import axios from 'axios';
import { User } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

interface SubmitAnswerPayload {
  text: string;
  questionId?: string;
  audioUrl?: string;
  code?: string;
}

type UserProfileUpdate = Partial<Pick<User, 'name' | 'email' | 'skills'>>;

// Add token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authService = {
  register: (email: string, password: string, name: string) =>
    apiClient.post('/auth/register', { email, password, name }),
  login: (email: string, password: string) =>
    apiClient.post('/auth/login', { email, password }),
  refresh: () => apiClient.post('/auth/refresh', {}),
};

export const interviewService = {
  startInterview: (difficulty: string, category: string) =>
    apiClient.post('/interviews', { difficulty, category }),
  startFromResume: (resumeText: string, difficulty: string) =>
    apiClient.post('/interviews/from-resume', { resumeText, difficulty }),
  getInterview: (id: string) => apiClient.get(`/interviews/${id}`),
  submitAnswer: (interviewId: string, answer: SubmitAnswerPayload) =>
    apiClient.post(`/interviews/${interviewId}/submit`, answer),
  completeInterview: (id: string) =>
    apiClient.post(`/interviews/${id}/complete`, {}),
  getHistory: () => apiClient.get('/interviews'),
};

export const questionService = {
  getNext: (interviewId: string) =>
    apiClient.get(`/questions/next?interview_id=${interviewId}`),
  generateFromResume: (resumeText: string) =>
    apiClient.post('/questions/from-resume', { resume: resumeText }),
};

export const evaluationService = {
  evaluateAnswer: (answer: string, question: string) =>
    apiClient.post('/evaluation/answer', { answer, question }),
  evaluateCode: (code: string, language: string) =>
    apiClient.post('/evaluation/code', { code, language }),
  getReport: (interviewId: string) =>
    apiClient.get(`/evaluation/report/${interviewId}`),
};

export const userService = {
  getProfile: () => apiClient.get('/users/profile'),
  updateProfile: (data: UserProfileUpdate) => apiClient.put('/users/profile', data),
  parseResumeText: (resumeText: string) =>
    apiClient.post('/users/resume/text', { resumeText }),
  uploadResume: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post('/users/resume', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getProgress: () => apiClient.get('/users/progress'),
};

export default apiClient;
