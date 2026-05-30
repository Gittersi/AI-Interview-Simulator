export interface User {
  id: string;
  email: string;
  name: string;
  skills: string[];
}

export interface Question {
  id: string;
  text: string;
  category: string;
  difficulty: 'easy' | 'medium' | 'hard';
  timeLimit: number;
}

export interface Interview {
  id: string;
  userId: string;
  startTime: Date;
  endTime?: Date;
  questions: Question[];
  answers: Answer[];
  status: 'in-progress' | 'completed' | 'abandoned';
}

export interface Answer {
  questionId: string;
  text: string;
  audioUrl?: string;
  code?: string;
  timestamp: Date;
}

export interface Evaluation {
  answerId: string;
  correctness: number;
  confidence: number;
  communication: number;
  feedback: string;
}

export interface PerformanceReport {
  interviewId: string;
  totalScore: number;
  correctnessScore: number;
  communicationScore: number;
  confidenceScore: number;
  evaluations: Evaluation[];
  suggestions: string[];
  timestamp: Date;
}
