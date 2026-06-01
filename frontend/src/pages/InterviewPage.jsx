import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { interviewService, evaluationService } from '../services/apiClient';
import { InterviewPanel } from '../components/InterviewPanel';
import { CodingEditor } from '../components/CodingEditor';
import { Clock, Sparkles } from 'lucide-react';

export const InterviewPage = () => {
  const { id } = useParams();
  const [interview, setInterview] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [timeLeft, setTimeLeft] = useState(0);
  const [isTimeLow, setIsTimeLow] = useState(false);

  useEffect(() => {
    const fetchInterview = async () => {
      try {
        if (id) {
          const response = await interviewService.getInterview(id);
          setInterview(response.data);
          
          if (response.data.questions && response.data.questions.length > 0) {
            setCurrentQuestion(response.data.questions[0]);
            setTimeLeft(response.data.questions[0].timeLimit);
          }
        }
      } catch (error) {
        console.error('Failed to fetch interview:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchInterview();
  }, [id]);

  // Timer effect
  useEffect(() => {
    if (timeLeft <= 0) {
      setIsTimeLow(false);
      return;
    }

    setIsTimeLow(timeLeft <= 20);
    const timer = setTimeout(() => {
      setTimeLeft(timeLeft - 1);
    }, 1000);

    return () => clearTimeout(timer);
  }, [timeLeft]);

  const handleSubmitAnswer = async (answer) => {
    try {
      if (!id) return;

      // Submit answer and use server-side evaluation if available
      const submitResp = await interviewService.submitAnswer(id, {
        text: answer,
        questionId: currentQuestion?.id,
      });

      let evaluation;
      if (submitResp && submitResp.data && submitResp.data.evaluation) {
        evaluation = submitResp.data.evaluation;
      } else if (currentQuestion) {
        // Fallback: call client-side evaluation
        const response = await evaluationService.evaluateAnswer(answer, currentQuestion.text);
        evaluation = response.data;
      }

      // Move to next question
      if (interview && questionIndex < interview.questions.length - 1) {
        const nextQuestion = interview.questions[questionIndex + 1];
        setCurrentQuestion(nextQuestion);
        setQuestionIndex(questionIndex + 1);
        setTimeLeft(nextQuestion.timeLimit);
      } else {
        // All questions completed
        if (id) {
          await interviewService.completeInterview(id);
        }
        alert('Interview completed! Generating report...');
      }

      return evaluation;
    } catch (error) {
      console.error('Failed to submit answer:', error);
      alert('Failed to submit answer. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-600">Loading interview...</p>
      </div>
    );
  }

  if (!currentQuestion) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-600">No questions available</p>
      </div>
    );
  }

  const totalQuestions = interview?.questions?.length || 0;
  const progressPercent = totalQuestions ? ((questionIndex + 1) / totalQuestions) * 100 : 0;
  const timeBarColor = isTimeLow ? 'bg-rose-500' : 'bg-emerald-500';

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-100 via-white to-slate-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      {/* Header */}
      <header className="bg-gradient-to-r from-indigo-600 to-sky-600 text-white shadow-lg sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 md:gap-0">
          <div>
            <h1 className="text-3xl font-bold">Interview Session</h1>
            <p className="text-sm text-sky-100 mt-1 flex items-center gap-2">
              <Sparkles className="w-4 h-4" /> Stay focused and answer clearly — the AI is listening.
            </p>
          </div>
          <div className="flex flex-col sm:flex-row sm:items-center gap-3">
            <div className="rounded-full bg-white/10 px-4 py-2 backdrop-blur-sm border border-white/20 text-sm font-semibold text-white flex items-center gap-2">
              <Clock className="w-4 h-4" />
              {Math.floor(timeLeft / 60)}:{String(timeLeft % 60).padStart(2, '0')}
            </div>
            <span className="rounded-full bg-white/15 px-4 py-2 text-sm text-white font-medium border border-white/20">
              Question {questionIndex + 1} of {totalQuestions}
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-10">
        <div className="max-w-3xl mx-auto mb-8">
          <div className="rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 shadow-xl transition-all duration-300 hover:-translate-y-1">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <h2 className="text-xl font-semibold text-slate-900 dark:text-white">Current Question Overview</h2>
                <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">Track progress and keep your pace while answering.</p>
              </div>
              <div className="text-right">
                <p className="text-sm uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">Progress</p>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">{Math.round(progressPercent)}%</p>
              </div>
            </div>
            <div className="mt-5 h-3 rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden">
              <div className={`h-full rounded-full ${timeBarColor}`} style={{ width: `${progressPercent}%` }} />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Question Panel */}
          <div>
            <InterviewPanel
              question={currentQuestion}
              onSubmitAnswer={handleSubmitAnswer}
            />
          </div>

          {/* Code Editor (for coding questions) */}
          {currentQuestion.category === 'coding' && (
            <div>
              <CodingEditor
                language="python"
                onExecute={async (code) => {
                  const result = await evaluationService.evaluateCode(code, 'python');
                  console.log('Code evaluation result:', result);
                }}
              />
            </div>
          )}
        </div>

        {/* Progress Indicator */}
        <div className="mt-12">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Progress</h3>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full transition-all"
                style={{
                  width: `${((questionIndex + 1) / (interview?.questions?.length || 1)) * 100}%`,
                }}
              ></div>
            </div>
            <p className="text-sm text-gray-600 mt-2">
              {questionIndex + 1} of {interview?.questions?.length || 0} questions completed
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};
