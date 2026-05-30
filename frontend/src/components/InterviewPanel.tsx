import React, { useState } from 'react';
import { Question } from '../types';
import { VoiceRecorder } from './VoiceRecorder';

interface InterviewPanelProps {
  question: Question;
  onSubmitAnswer: (answer: string, audioUrl?: string) => Promise<AnswerFeedback | void>;
}

interface AnswerFeedback {
  feedback?: string;
  llm_feedback?: string;
}

export const InterviewPanel: React.FC<InterviewPanelProps> = ({
  question,
  onSubmitAnswer,
}) => {
  const [answer, setAnswer] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedback, setFeedback] = useState('');

  const handleSubmit = async () => {
    if (!answer.trim()) {
      alert('Please provide an answer');
      return;
    }

    setIsSubmitting(true);
    try {
      const result = await onSubmitAnswer(answer);
      setFeedback(result?.llm_feedback || result?.feedback || '');
      setAnswer('');
    } catch (error) {
      console.error('Failed to submit answer:', error);
      alert('Failed to submit answer. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleVoiceTranscription = (text: string) => {
    setAnswer((prev) => (prev ? prev + ' ' + text : text));
  };

  return (
    <div className="flex flex-col gap-6 p-6 bg-white rounded-lg shadow-lg">
      <div className="bg-blue-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">Question</h3>
        <p className="text-gray-700 text-base leading-relaxed">{question.text}</p>
        <div className="flex gap-4 mt-3 text-sm">
          <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded">
            {question.category}
          </span>
          <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded">
            Difficulty: {question.difficulty}
          </span>
          <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded">
            Time: {question.timeLimit}s
          </span>
        </div>
      </div>

      <div className="space-y-3">
        <label className="block">
          <span className="text-sm font-medium text-gray-700 mb-2 block">
            Your Answer
          </span>
          <textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Type your answer here or use the voice recorder below..."
            className="w-full h-40 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          />
        </label>
      </div>

      <VoiceRecorder
        onTranscription={handleVoiceTranscription}
        disabled={isSubmitting}
      />

      {feedback && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
          <h4 className="text-sm font-semibold text-green-800 mb-1">Feedback</h4>
          <p className="text-sm text-green-700">{feedback}</p>
        </div>
      )}

      <button
        onClick={handleSubmit}
        disabled={isSubmitting || !answer.trim()}
        className="w-full py-3 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white font-semibold rounded-lg transition-all"
      >
        {isSubmitting ? 'Submitting...' : 'Submit Answer'}
      </button>
    </div>
  );
};
