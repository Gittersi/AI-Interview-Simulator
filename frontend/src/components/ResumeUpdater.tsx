import React, { useState } from 'react';
import { userService } from '../services/apiClient';
import { CheckCircle, Clipboard, Edit3, RefreshCcw } from 'lucide-react';

interface UpdateResponse {
  updatedResume: string;
  analysis: {
    summary: string;
    suggestions: string[];
    keywords_added?: string[];
    keywords_missing?: string[];
    job_match_score?: number;
  };
}

export const ResumeUpdater: React.FC = () => {
  const [resumeText, setResumeText] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [updatedResume, setUpdatedResume] = useState('');
  const [analysis, setAnalysis] = useState<UpdateResponse['analysis'] | null>(null);
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [savedMessage, setSavedMessage] = useState('');

  const handleUpdateResume = async () => {
    setError(null);
    setSavedMessage('');
    setUpdatedResume('');
    setAnalysis(null);

    if (!resumeText.trim() || !jobDescription.trim()) {
      setError('Please add both your resume text and the job description.');
      return;
    }

    setIsUpdating(true);
    try {
      const response = await userService.updateResume(resumeText, jobDescription);
      const data = response.data as UpdateResponse;
      setUpdatedResume(data.updatedResume);
      setAnalysis(data.analysis);
      setSavedMessage('Updated resume generated successfully.');
    } catch (err) {
      console.error('Resume update failed:', err);
      setError('Failed to update resume. Please try again.');
    } finally {
      setIsUpdating(false);
    }
  };

  const handleCopy = async () => {
    if (!updatedResume) {
      return;
    }

    try {
      await navigator.clipboard.writeText(updatedResume);
      setSavedMessage('Updated resume copied to clipboard.');
    } catch (err) {
      setError('Unable to copy resume. Please copy it manually.');
    }
  };

  const handleClear = () => {
    setResumeText('');
    setJobDescription('');
    setUpdatedResume('');
    setAnalysis(null);
    setError(null);
    setSavedMessage('');
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3 mb-6">
        <Edit3 className="w-6 h-6 text-blue-500" />
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Resume Tailoring Dashboard</h2>
          <p className="text-sm text-gray-600">
            Automatically rewrite your resume to better match the role described in the job description.
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="space-y-4 bg-white p-6 rounded-lg shadow">
          <label className="block">
            <span className="block text-sm font-medium text-gray-700 mb-2">Current Resume Text</span>
            <textarea
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              placeholder="Paste your resume here..."
              className="w-full h-44 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              disabled={isUpdating}
            />
          </label>

          <label className="block">
            <span className="block text-sm font-medium text-gray-700 mb-2">Job Description</span>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the job description to tailor your resume to the role..."
              className="w-full h-44 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              disabled={isUpdating}
            />
          </label>

          {error && (
            <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
              <RefreshCcw className="w-5 h-5 text-red-600" />
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <div className="flex flex-wrap gap-3">
            <button
              onClick={handleUpdateResume}
              disabled={isUpdating || !resumeText.trim() || !jobDescription.trim()}
              className="py-3 px-5 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold rounded-lg"
            >
              {isUpdating ? 'Updating resume...' : 'Update Resume'}
            </button>
            <button
              onClick={handleClear}
              disabled={isUpdating}
              className="py-3 px-5 bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold rounded-lg"
            >
              Clear
            </button>
          </div>
        </div>

        <div className="space-y-4 bg-gray-50 p-6 rounded-lg border border-gray-200">
          <div className="rounded-lg bg-white p-4 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-800">How this works</h3>
            <ul className="mt-3 space-y-2 text-sm text-gray-600">
              <li>1. Paste your current resume text.</li>
              <li>2. Add the job description for the role you want.</li>
              <li>3. Generate a tailored resume optimized for ATS matching.</li>
            </ul>
          </div>

          <div className="rounded-lg bg-white p-4 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-800">Tips</h3>
            <p className="text-sm text-gray-600">Use clear section headers and avoid tables or images for better ATS readability.</p>
          </div>

          {savedMessage && (
            <div className="flex items-start gap-3 p-4 bg-green-50 border border-green-200 rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <p className="text-sm text-green-800">{savedMessage}</p>
            </div>
          )}
        </div>
      </div>

      {analysis && (
        <div className="bg-white rounded-lg shadow p-6 space-y-5">
          <div className="flex flex-col gap-2">
            <h3 className="text-xl font-semibold text-gray-800">Update Summary</h3>
            <p className="text-gray-600">{analysis.summary}</p>
          </div>

          {analysis.job_match_score !== undefined && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="text-sm font-medium text-gray-700">Estimated Job Match</p>
                <p className="text-3xl font-bold text-blue-700">{analysis.job_match_score}%</p>
              </div>
              <div className="p-4 bg-white rounded-lg border border-gray-200">
                <p className="text-sm font-medium text-gray-700">Missing Keywords</p>
                {analysis.keywords_missing?.length ? (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {analysis.keywords_missing.map((keyword) => (
                      <span key={keyword} className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm">
                        {keyword}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-600">No missing keywords detected.</p>
                )}
              </div>
            </div>
          )}

          <div>
            <h4 className="text-lg font-semibold text-gray-800 mb-3">Suggested Improvements</h4>
            <ul className="list-disc list-inside space-y-2 text-gray-600">
              {analysis.suggestions.map((item, index) => (
                <li key={`${item}-${index}`}>{item}</li>
              ))}
            </ul>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between gap-3">
              <h4 className="text-lg font-semibold text-gray-800">Updated Resume</h4>
              <button
                onClick={handleCopy}
                disabled={!updatedResume}
                className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 text-white rounded-lg"
              >
                <Clipboard className="w-4 h-4" /> Copy
              </button>
            </div>
            <textarea
              value={updatedResume}
              readOnly
              className="w-full h-64 p-4 border border-gray-300 rounded-lg bg-gray-50 resize-none"
            />
          </div>
        </div>
      )}
    </div>
  );
};
