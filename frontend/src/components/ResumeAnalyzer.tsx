import React, { useState } from 'react';
import { userService } from '../services/apiClient';
import { BarChart3, AlertCircle, CheckCircle, TrendingUp } from 'lucide-react';

interface ATSAnalysis {
  ats_score: number;
  ats_grade: string;
  formatting_score: number;
  keyword_score: number;
  content_quality_score: number;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  improvements: Array<{ category: string; suggestion: string }>;
  keywords_found: string[];
  keywords_missing: string[];
  formatting_issues: string[];
  job_match_score?: number;
}

interface ResumeAnalyzerProps {
  onAnalysisComplete?: (analysis: ATSAnalysis) => void;
}

export const ResumeAnalyzer: React.FC<ResumeAnalyzerProps> = ({ onAnalysisComplete }) => {
  const [resumeText, setResumeText] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<ATSAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showJobDescription, setShowJobDescription] = useState(false);

  const getScoreColor = (score: number): string => {
    if (score >= 85) return 'text-green-600';
    if (score >= 70) return 'text-blue-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number): string => {
    if (score >= 85) return 'bg-green-50';
    if (score >= 70) return 'bg-blue-50';
    if (score >= 60) return 'bg-yellow-50';
    return 'bg-red-50';
  };

  const getGradeColor = (grade: string): string => {
    switch (grade) {
      case 'A':
        return 'bg-green-600 text-white';
      case 'B':
        return 'bg-blue-600 text-white';
      case 'C':
        return 'bg-yellow-600 text-white';
      case 'D':
        return 'bg-orange-600 text-white';
      default:
        return 'bg-red-600 text-white';
    }
  };

  const handleAnalyze = async () => {
    try {
      setError(null);
      setIsAnalyzing(true);

      if (!resumeText.trim()) {
        throw new Error('Please enter your resume text');
      }

      if (resumeText.trim().length < 100) {
        throw new Error('Resume text is too short (minimum 100 characters)');
      }

      const response = await userService.analyzeResumeATS(
        resumeText,
        showJobDescription ? jobDescription : undefined
      );

      const atsAnalysis = response.data.analysis as ATSAnalysis;
      setAnalysis(atsAnalysis);
      onAnalysisComplete?.(atsAnalysis);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to analyze resume. Please try again.');
      }
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleClear = () => {
    setResumeText('');
    setJobDescription('');
    setAnalysis(null);
    setError(null);
  };

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <div className="bg-white dark:bg-slate-900 rounded-lg shadow-sm dark:shadow-lg p-6 border border-gray-200 dark:border-slate-700 transition-colors duration-300">
        <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
          <BarChart3 className="w-6 h-6" />
          Resume ATS Analyzer
        </h2>

        <div className="space-y-4">
          {/* Resume Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Your Resume
              <span className="text-red-500 ml-1">*</span>
            </label>
            <textarea
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              placeholder="Paste your entire resume text here..."
              className="w-full h-40 p-4 border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-colors duration-300"
              disabled={isAnalyzing}
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {resumeText.length} characters ({Math.ceil(resumeText.length / 5)} words)
            </p>
          </div>

          {/* Job Description Toggle */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="showJobDesc"
              checked={showJobDescription}
              onChange={(e) => setShowJobDescription(e.target.checked)}
              disabled={isAnalyzing}
              className="rounded"
            />
            <label htmlFor="showJobDesc" className="text-sm font-medium text-gray-700">
              Include job description for better matching (optional)
            </label>
          </div>

          {/* Job Description Input */}
          {showJobDescription && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Job Description
              </label>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste the job description here for better ATS matching..."
                className="w-full h-32 p-4 border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-colors duration-300"
                disabled={isAnalyzing}
              />
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="flex items-start gap-3 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg transition-colors duration-300">
              <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-800 dark:text-red-300">{error}</p>
            </div>
          )}

          {/* Buttons */}
          <div className="flex gap-3 pt-4">
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing || !resumeText.trim()}
              className="flex-1 py-3 bg-blue-600 hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-700 disabled:bg-gray-400 dark:disabled:bg-gray-600 text-white font-semibold rounded-lg transition-colors duration-300"
            >
              {isAnalyzing ? 'Analyzing...' : 'Analyze ATS Score'}
            </button>
            <button
              onClick={handleClear}
              disabled={isAnalyzing}
              className="px-6 py-3 bg-gray-200 dark:bg-slate-700 hover:bg-gray-300 dark:hover:bg-slate-600 text-gray-800 dark:text-gray-200 font-semibold rounded-lg transition-colors duration-300"
            >
              Clear
            </button>
          </div>
        </div>
      </div>

      {/* Results Section */}
      {analysis && (
        <div className="space-y-6">
          {/* Score Overview */}
          <div className="bg-gradient-to-br from-blue-50 dark:from-slate-900 to-indigo-50 dark:to-slate-800 rounded-lg shadow-sm dark:shadow-lg p-6 border border-gray-200 dark:border-slate-700 transition-colors duration-300">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              {/* Main ATS Score */}
              <div className="flex flex-col items-center p-4 bg-white dark:bg-slate-800 rounded-lg shadow-sm dark:shadow-md transition-colors duration-300">
                <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">ATS Score</p>
                <div className={`text-5xl font-bold ${getScoreColor(analysis.ats_score)} my-2`}>
                  {analysis.ats_score}
                </div>
                <div className={`text-lg font-bold px-3 py-1 rounded-full ${getGradeColor(analysis.ats_grade)}`}>
                  {analysis.ats_grade}
                </div>
              </div>

              {/* Component Scores */}
              {[
                { label: 'Formatting', score: analysis.formatting_score },
                { label: 'Keywords', score: analysis.keyword_score },
                { label: 'Content', score: analysis.content_quality_score },
              ].map((item) => (
                <div key={item.label} className="flex flex-col items-center p-4 bg-white dark:bg-slate-800 rounded-lg shadow-sm dark:shadow-md transition-colors duration-300">
                  <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">{item.label}</p>
                  <p className={`text-3xl font-bold ${getScoreColor(item.score)} my-2`}>
                    {item.score}
                  </p>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${
                        item.score >= 80
                          ? 'bg-green-500'
                          : item.score >= 60
                          ? 'bg-yellow-500'
                          : 'bg-red-500'
                      }`}
                      style={{ width: `${item.score}%` }}
                    />
                  </div>
                </div>
              ))}

              {/* Job Match Score */}
              {analysis.job_match_score !== undefined && analysis.job_match_score !== null && (
                <div className="flex flex-col items-center p-4 bg-white dark:bg-slate-800 rounded-lg shadow-sm dark:shadow-md transition-colors duration-300">
                  <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">Job Match</p>
                  <p className={`text-3xl font-bold ${getScoreColor(analysis.job_match_score)} my-2`}>
                    {analysis.job_match_score}
                  </p>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="h-2 rounded-full bg-purple-500 transition-all"
                      style={{ width: `${analysis.job_match_score}%` }}
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Summary */}
            <div className="mt-6 p-4 bg-white dark:bg-slate-800 rounded-lg transition-colors duration-300">
              <p className="text-gray-800 dark:text-gray-200">{analysis.summary}</p>
            </div>
          </div>

          {/* Strengths */}
          {analysis.strengths.length > 0 && (
            <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-6 transition-colors duration-300">
              <h3 className="text-lg font-semibold text-green-800 dark:text-green-300 mb-4 flex items-center gap-2">
                <CheckCircle className="w-5 h-5" />
                Strengths
              </h3>
              <ul className="space-y-2">
                {analysis.strengths.map((strength, i) => (
                  strength && (
                    <li key={i} className="flex items-start gap-2 text-green-700">
                      <span className="text-green-600 font-bold mt-0.5">✓</span>
                      <span>{strength}</span>
                    </li>
                  )
                ))}
              </ul>
            </div>
          )}

          {/* Weaknesses */}
          {analysis.weaknesses.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-red-800 mb-4 flex items-center gap-2">
                <AlertCircle className="w-5 h-5" />
                Areas for Improvement
              </h3>
              <ul className="space-y-2">
                {analysis.weaknesses.map((weakness, i) => (
                  weakness && (
                    <li key={i} className="flex items-start gap-2 text-red-700">
                      <span className="text-red-600 font-bold mt-0.5">!</span>
                      <span>{weakness}</span>
                    </li>
                  )
                ))}
              </ul>
            </div>
          )}

          {/* Recommendations */}
          {analysis.improvements.length > 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-blue-800 mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Recommendations
              </h3>
              <div className="space-y-3">
                {analysis.improvements.map((improvement, i) => (
                  <div key={i} className="bg-white p-4 rounded-lg border border-blue-100">
                    <p className="text-sm font-semibold text-blue-900 capitalize">
                      {improvement.category}
                    </p>
                    <p className="text-sm text-blue-800 mt-1">{improvement.suggestion}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Keywords */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Keywords Found */}
            {analysis.keywords_found.length > 0 && (
              <div className="bg-white border border-green-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-3">Keywords Found</h3>
                <div className="flex flex-wrap gap-2">
                  {analysis.keywords_found.map((keyword, i) => (
                    <span
                      key={i}
                      className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full font-medium"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Keywords Missing */}
            {analysis.keywords_missing.length > 0 && (
              <div className="bg-white dark:bg-slate-900 border border-amber-200 dark:border-amber-800 rounded-lg p-6 transition-colors duration-300">
                <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-3">Missing Keywords</h3>
                <div className="flex flex-wrap gap-2">
                  {analysis.keywords_missing.map((keyword, i) => (
                    <span
                      key={i}
                      className="px-3 py-1 bg-amber-100 dark:bg-amber-900 text-amber-800 dark:text-amber-300 text-sm rounded-full font-medium transition-colors duration-300"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Formatting Issues */}
          {analysis.formatting_issues.length > 0 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-yellow-800 mb-3">Formatting Issues</h3>
              <ul className="space-y-2">
                {analysis.formatting_issues.map((issue, i) => (
                  <li key={i} className="flex items-start gap-2 text-yellow-800">
                    <span className="text-yellow-600 font-bold mt-0.5">•</span>
                    <span>{issue}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
