import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store';
import { interviewService, userService } from '../services/apiClient';
import { BarChart3, FileText, LogOut, Upload } from 'lucide-react';

interface ParsedResume {
  skills: string[];
  experience: string[];
  education: string[];
}

export const Dashboard: React.FC = () => {
  const [interviews, setInterviews] = useState<any[]>([]);
  const [progress, setProgress] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [resumeText, setResumeText] = useState('');
  const [resumeDifficulty, setResumeDifficulty] = useState('medium');
  const [parsedResume, setParsedResume] = useState<ParsedResume | null>(null);
  const [resumeStatus, setResumeStatus] = useState('');
  const [resumeError, setResumeError] = useState('');
  const [isParsingResume, setIsParsingResume] = useState(false);
  const [isStartingResumeInterview, setIsStartingResumeInterview] = useState(false);
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [interviewsRes, progressRes] = await Promise.all([
          interviewService.getHistory(),
          userService.getProgress(),
        ]);
        setInterviews(interviewsRes.data);
        setProgress(progressRes.data);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleStartInterview = async (difficulty: string) => {
    try {
      const response = await interviewService.startInterview(difficulty, 'algorithms');
      navigate(`/interview/${response.data.id}`);
    } catch (error) {
      console.error('Failed to start interview:', error);
      alert('Failed to start interview. Please try again.');
    }
  };

  const handleResumeFile = async (file: File) => {
    const text = await file.text();
    setResumeText(text);
    setParsedResume(null);
    setResumeStatus('');
    setResumeError('');
  };

  const handleParseResume = async () => {
    if (resumeText.trim().length < 20) {
      setResumeError('Paste a little more resume text first.');
      return;
    }

    setIsParsingResume(true);
    setResumeError('');
    setResumeStatus('');

    try {
      const response = await userService.parseResumeText(resumeText);
      setParsedResume(response.data);
      setResumeStatus('Skills extracted. Ready to generate an interview.');
    } catch (error) {
      console.error('Failed to parse resume:', error);
      setResumeError('Could not parse the resume. Check the text and try again.');
    } finally {
      setIsParsingResume(false);
    }
  };

  const handleStartResumeInterview = async () => {
    if (resumeText.trim().length < 20) {
      setResumeError('Paste or upload resume text before starting.');
      return;
    }

    setIsStartingResumeInterview(true);
    setResumeError('');

    try {
      const response = await interviewService.startFromResume(resumeText, resumeDifficulty);
      navigate(`/interview/${response.data.id}`);
    } catch (error) {
      console.error('Failed to start resume interview:', error);
      setResumeError('Could not generate resume-based questions. Please try again.');
    } finally {
      setIsStartingResumeInterview(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-600">Loading...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <BarChart3 className="w-8 h-8 text-blue-500" />
            <h1 className="text-2xl font-bold text-gray-800">AI Interview Simulator</h1>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-gray-700">Welcome, {user?.name}</span>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-12">
        {/* Progress Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white p-6 rounded-lg shadow">
            <p className="text-gray-600 text-sm mb-2">Total Interviews</p>
            <p className="text-4xl font-bold text-blue-600">
              {progress?.totalInterviews || 0}
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <p className="text-gray-600 text-sm mb-2">Completed</p>
            <p className="text-4xl font-bold text-green-600">
              {progress?.completedInterviews || 0}
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <p className="text-gray-600 text-sm mb-2">Average Score</p>
            <p className="text-4xl font-bold text-purple-600">
              {progress?.averageScore?.toFixed(1) || 0}%
            </p>
          </div>
        </div>

        {/* Start Interview Section */}
        <div className="bg-white rounded-lg shadow p-8 mb-12">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Start New Interview</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {['easy', 'medium', 'hard'].map((difficulty) => (
              <button
                key={difficulty}
                onClick={() => handleStartInterview(difficulty)}
                className={`py-4 px-6 rounded-lg font-semibold text-white capitalize transition-all ${
                  difficulty === 'easy'
                    ? 'bg-green-500 hover:bg-green-600'
                    : difficulty === 'medium'
                    ? 'bg-yellow-500 hover:bg-yellow-600'
                    : 'bg-red-500 hover:bg-red-600'
                }`}
              >
                {difficulty} Interview
              </button>
            ))}
          </div>
        </div>

        {/* Resume Interview Section */}
        <div className="bg-white rounded-lg shadow p-8 mb-12">
          <div className="flex items-center gap-3 mb-6">
            <FileText className="w-6 h-6 text-blue-500" />
            <h2 className="text-2xl font-bold text-gray-800">Resume-Based Interview</h2>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-4">
              <label className="block">
                <span className="text-sm font-medium text-gray-700 mb-2 block">
                  Paste resume text
                </span>
                <textarea
                  value={resumeText}
                  onChange={(event) => {
                    setResumeText(event.target.value);
                    setParsedResume(null);
                    setResumeStatus('');
                    setResumeError('');
                  }}
                  placeholder="Paste your resume content here..."
                  className="w-full h-56 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                />
              </label>

              <div className="flex flex-wrap items-center gap-3">
                <label className="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                  <Upload className="w-4 h-4" />
                  <span className="text-sm font-medium text-gray-700">Upload .txt resume</span>
                  <input
                    type="file"
                    accept=".txt,text/plain"
                    className="hidden"
                    onChange={(event) => {
                      const file = event.target.files?.[0];
                      if (file) {
                        handleResumeFile(file);
                      }
                    }}
                  />
                </label>

                <select
                  value={resumeDifficulty}
                  onChange={(event) => setResumeDifficulty(event.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg capitalize focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>

                <button
                  onClick={handleParseResume}
                  disabled={isParsingResume || resumeText.trim().length < 20}
                  className="px-5 py-2 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white font-semibold rounded-lg"
                >
                  {isParsingResume ? 'Extracting...' : 'Extract Skills'}
                </button>

                <button
                  onClick={handleStartResumeInterview}
                  disabled={isStartingResumeInterview || resumeText.trim().length < 20}
                  className="px-5 py-2 bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white font-semibold rounded-lg"
                >
                  {isStartingResumeInterview ? 'Generating...' : 'Start Resume Interview'}
                </button>
              </div>

              {resumeStatus && <p className="text-sm text-green-700">{resumeStatus}</p>}
              {resumeError && <p className="text-sm text-red-600">{resumeError}</p>}
            </div>

            <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Extracted Skills</h3>
              {parsedResume?.skills.length ? (
                <div className="flex flex-wrap gap-2">
                  {parsedResume.skills.map((skill) => (
                    <span
                      key={skill}
                      className="px-3 py-1 bg-blue-100 text-blue-700 rounded text-sm font-medium"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-600">
                  Extract skills to preview what the interview will focus on.
                </p>
              )}

              {parsedResume?.experience.length ? (
                <div className="mt-5">
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">Experience Signals</h4>
                  <ul className="space-y-1 text-sm text-gray-600">
                    {parsedResume.experience.slice(0, 4).map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </div>
          </div>
        </div>

        {/* Recent Interviews */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="p-6 border-b">
            <h2 className="text-2xl font-bold text-gray-800">Recent Interviews</h2>
          </div>
          {interviews.length === 0 ? (
            <div className="p-6 text-center text-gray-600">
              No interviews yet. Start one to see your history!
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Date</th>
                    <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Category</th>
                    <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Difficulty</th>
                    <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Status</th>
                    <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {interviews.map((interview) => (
                    <tr key={interview.id} className="border-t hover:bg-gray-50">
                      <td className="px-6 py-3 text-sm text-gray-600">
                        {new Date(interview.startTime).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-3 text-sm text-gray-600">{interview.category}</td>
                      <td className="px-6 py-3 text-sm">
                        <span className={`px-3 py-1 rounded text-sm font-medium ${
                          interview.difficulty === 'easy' ? 'bg-green-100 text-green-700' :
                          interview.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                          'bg-red-100 text-red-700'
                        }`}>
                          {interview.difficulty}
                        </span>
                      </td>
                      <td className="px-6 py-3 text-sm">
                        <span className={`px-3 py-1 rounded text-sm font-medium ${
                          interview.status === 'completed' ? 'bg-blue-100 text-blue-700' :
                          'bg-yellow-100 text-yellow-700'
                        }`}>
                          {interview.status}
                        </span>
                      </td>
                      <td className="px-6 py-3 text-sm">
                        {interview.status === 'completed' ? (
                          <button
                            onClick={() => navigate(`/report/${interview.id}`)}
                            className="text-blue-600 hover:text-blue-800 font-semibold"
                          >
                            View Report
                          </button>
                        ) : (
                          <span className="text-gray-500">In Progress</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};
