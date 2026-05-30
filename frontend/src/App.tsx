import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore, useThemeStore } from './store';
import { LoginPage } from './pages/LoginPage';
import { Dashboard } from './pages/Dashboard';
import { InterviewPage } from './pages/InterviewPage';
import { ReportPage } from './pages/ReportPage';
import { ResumeAnalysisPage } from './pages/ResumeAnalysisPage';
import './index.css';

function App() {
  const { token } = useAuthStore();
  const { isDarkMode } = useThemeStore();

  return (
    <Router>
      <div className={`min-h-screen ${isDarkMode ? 'dark' : ''} bg-white dark:bg-slate-950 text-gray-900 dark:text-gray-100 transition-colors duration-300`}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/dashboard" element={token ? <Dashboard /> : <Navigate to="/login" />} />
          <Route path="/interview/:id" element={token ? <InterviewPage /> : <Navigate to="/login" />} />
          <Route path="/report/:id" element={token ? <ReportPage /> : <Navigate to="/login" />} />
          <Route path="/resume-analysis" element={token ? <ResumeAnalysisPage /> : <Navigate to="/login" />} />
          <Route path="/" element={<Navigate to={token ? '/dashboard' : '/login'} />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
