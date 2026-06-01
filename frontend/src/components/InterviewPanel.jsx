import React, { useState } from 'react';
import { VoiceRecorder } from './VoiceRecorder';
import { Volume2, VolumeX } from 'lucide-react';
import { speechService } from '../services/speechService';

export const InterviewPanel = ({
  question,
  onSubmitAnswer,
}) => {
  const [answer, setAnswer] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [scores, setScores] = useState({});

  const handleSubmit = async () => {
    if (!answer.trim()) {
      alert('Please provide an answer');
      return;
    }

    setIsSubmitting(true);
    try {
      const result = await onSubmitAnswer(answer);
      const feedbackText = result?.llm_feedback || result?.feedback || '';
      setFeedback(feedbackText);
      
      if (result) {
        setScores({
          correctness: result.correctness,
          confidence: result.confidence,
          communication: result.communication,
        });
      }
      
      setAnswer('');
    } catch (error) {
      console.error('Failed to submit answer:', error);
      alert('Failed to submit answer. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePlayFeedback = async () => {
    if (!feedback || isSpeaking) return;
    
    try {
      setIsSpeaking(true);
      await speechService.textToSpeech(feedback);
    } catch (error) {
      console.error('Failed to play feedback:', error);
      alert('Could not play audio feedback. Check your browser settings.');
    } finally {
      setIsSpeaking(false);
    }
  };

  const handleStopSpeech = () => {
    speechService.stopSpeech();
    setIsSpeaking(false);
  };

  const hasTTSSupport = speechService.checkSpeechSynthesisSupport();

  return (
    <div className="flex flex-col gap-6 p-6 bg-white rounded-3xl shadow-2xl border border-slate-200 dark:bg-slate-900 dark:border-slate-800 transition-all duration-300 hover:-translate-y-0.5">
      <div className="bg-gradient-to-r from-sky-50 to-blue-50 dark:from-slate-800 dark:to-slate-900 p-5 rounded-3xl border border-slate-200 dark:border-slate-700">
        <div className="flex flex-col gap-3">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Question</h3>
          <p className="text-gray-700 dark:text-slate-200 text-base leading-relaxed">{question.text}</p>
        </div>
        <div className="flex flex-wrap gap-2 mt-4">
          <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-200 text-sm rounded-full font-medium transition-all duration-300 hover:scale-105">
            {question.category}
          </span>
          <span className="px-3 py-1 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-sm rounded-full font-medium transition-all duration-300 hover:scale-105">
            Difficulty: {question.difficulty}
          </span>
          <span className="px-3 py-1 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-sm rounded-full font-medium transition-all duration-300 hover:scale-105">
            Time: {question.timeLimit}s
          </span>
        </div>
      </div>

      <div className="space-y-3">
        <label className="block">
          <span className="text-sm font-medium text-gray-700 mb-2 block">Your Answer</span>
          <textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Type your answer here or use the voice recorder below..."
            className="w-full h-40 p-3 border border-gray-300 rounded-3xl focus:ring-4 focus:ring-blue-200 focus:border-transparent resize-none transition-all duration-300 bg-white dark:bg-slate-900 dark:text-slate-100"
            disabled={isSubmitting}
          />
        </label>
        <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
          <p>{answer.length} characters</p>
          <p className="italic">Pro tip: keep answers concise and structured.</p>
        </div>
      </div>

      <VoiceRecorder
        onTranscription={(text) => setAnswer((prev) => (prev ? `${prev} ${text}` : text))}
        disabled={isSubmitting}
      />

      {feedback && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-3xl transition-all duration-300">
          <div className="flex items-start justify-between mb-2">
            <h4 className="text-sm font-semibold text-green-800">Feedback</h4>
            {hasTTSSupport && (
              <button
                onClick={isSpeaking ? handleStopSpeech : handlePlayFeedback}
                disabled={!feedback}
                className={`p-2 rounded-full transition-all ${
                  isSpeaking
                    ? 'bg-red-100 text-red-600 hover:bg-red-200'
                    : 'bg-green-100 text-green-600 hover:bg-green-200'
                }`}
                title={isSpeaking ? 'Stop audio' : 'Play audio'}
              >
                {isSpeaking ? (
                  <VolumeX className="w-4 h-4" />
                ) : (
                  <Volume2 className="w-4 h-4" />
                )}
              </button>
            )}
          </div>
          <p className="text-sm text-green-700 leading-relaxed">{feedback}</p>
          
          {Object.keys(scores).length > 0 && (
            <div className="mt-3 pt-3 border-t border-green-200">
              <div className="grid grid-cols-3 gap-2">
                {scores.correctness !== undefined && (
                  <div className="text-center">
                    <p className="text-xs text-green-600 font-medium">Correctness</p>
                    <p className="text-lg font-bold text-green-700">{Math.round(scores.correctness)}%</p>
                  </div>
                )}
                {scores.confidence !== undefined && (
                  <div className="text-center">
                    <p className="text-xs text-green-600 font-medium">Confidence</p>
                    <p className="text-lg font-bold text-green-700">{Math.round(scores.confidence)}%</p>
                  </div>
                )}
                {scores.communication !== undefined && (
                  <div className="text-center">
                    <p className="text-xs text-green-600 font-medium">Communication</p>
                    <p className="text-lg font-bold text-green-700">{Math.round(scores.communication)}%</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      <button
        onClick={handleSubmit}
        disabled={isSubmitting || !answer.trim()}
        className="w-full py-3 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white font-semibold rounded-3xl transition-all duration-300 shadow-lg hover:-translate-y-0.5"
      >
        {isSubmitting ? 'Submitting...' : 'Submit Answer'}
      </button>
    </div>
  );
};
