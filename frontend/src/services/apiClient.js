import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    if (!config.headers) config.headers = {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authService = {
  register: (email, password, name) =>
    apiClient.post('/auth/register', { email, password, name }),
  login: (email, password) =>
    apiClient.post('/auth/login', { email, password }),
  refresh: () => apiClient.post('/auth/refresh', {}),
};

export const interviewService = {
  startInterview: (difficulty, category) =>
    apiClient.post('/interviews', { difficulty, category }),
  startFromResume: (resumeText, difficulty) =>
    apiClient.post('/interviews/from-resume', { resumeText, difficulty }),
  getInterview: (id) => apiClient.get(`/interviews/${id}`),
  submitAnswer: (interviewId, answer) =>
    apiClient.post(`/interviews/${interviewId}/submit`, answer),
  completeInterview: (id) =>
    apiClient.post(`/interviews/${id}/complete`, {}),
  getHistory: () => apiClient.get('/interviews'),
};

export const questionService = {
  getNext: (interviewId) =>
    apiClient.get(`/questions/next?interview_id=${interviewId}`),
  generateFromResume: (resumeText) =>
    apiClient.post('/questions/from-resume', { resume: resumeText }),
  generateRandom: (category, difficulty, count = 5) =>
    apiClient.post('/questions/random', { category, difficulty, count }),
};

export const evaluationService = {
  evaluateAnswer: (answer, question) =>
    apiClient.post('/evaluation/answer', { answer, question }),
  evaluateCode: (code, language) =>
    apiClient.post('/evaluation/code', { code, language }),
  getReport: (interviewId) =>
    apiClient.get(`/evaluation/report/${interviewId}`),
};

export const userService = {
  getProfile: () => apiClient.get('/users/profile'),
  updateProfile: (data) => apiClient.put('/users/profile', data),
  parseResumeText: (resumeText) =>
    apiClient.post('/users/resume/text', { resumeText }),
  analyzeResumeATS: (resumeText, jobDescription) =>
    apiClient.post('/users/resume/analyze-ats', { resumeText, jobDescription }),
  updateResume: (resumeText, jobDescription) =>
    apiClient.post('/users/resume/update', { resumeText, jobDescription }),
  uploadResume: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post('/users/resume', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getProgress: () => apiClient.get('/users/progress'),
};

export default apiClient;
