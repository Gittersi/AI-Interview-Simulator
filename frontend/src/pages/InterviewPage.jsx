import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { interviewService, evaluationService } from '../services/apiClient';
import { InterviewPanel } from '../components/InterviewPanel';
import { CodingEditor } from '../components/CodingEditor';
import { Clock } from 'lucide-react';

export const InterviewPage = () => {
  const { id } = useParams();
  const [interview, setInterview] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [timeLeft, setTimeLeft] = useState(0);

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
    if (timeLeft <= 0) return;

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

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-800">Interview Session</h1>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-red-500" />
              <span className="text-lg font-semibold text-gray-700">
                {Math.floor(timeLeft / 60)}:{String(timeLeft % 60).padStart(2, '0')}
              </span>
            </div>
            <span className="text-gray-600">
              Question {questionIndex + 1} of {interview?.questions?.length || 0}
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
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
