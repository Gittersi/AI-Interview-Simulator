import React from 'react';
import { ResumeAnalyzer } from '../components/ResumeAnalyzer';

export const ResumeAnalysisPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Resume ATS Score Analyzer
          </h1>
          <p className="text-lg text-gray-600">
            Get an instant ATS score for your resume and receive AI-powered recommendations
            to improve your chances with applicant tracking systems
          </p>
        </div>

        {/* Main Content */}
        <ResumeAnalyzer
          onAnalysisComplete={(analysis) => {
            console.log('Analysis completed:', analysis);
          }}
        />

        {/* Tips Section */}
        <div className="mt-12 bg-white rounded-lg shadow p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Tips to Improve Your ATS Score</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Formatting Tips */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-3 text-blue-600">
                📋 Formatting Best Practices
              </h3>
              <ul className="space-y-2 text-gray-700">
                <li>✓ Use simple, clean formatting (no tables or graphics)</li>
                <li>✓ Stick to standard fonts (Arial, Calibri, Times New Roman)</li>
                <li>✓ Use clear section headings (Experience, Education, Skills)</li>
                <li>✓ Save as PDF or .docx for better compatibility</li>
                <li>✓ Avoid headers, footers, and complex layouts</li>
                <li>✓ Keep margins between 0.5" and 1"</li>
              </ul>
            </div>

            {/* Keyword Tips */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-3 text-green-600">
                🎯 Keyword Optimization
              </h3>
              <ul className="space-y-2 text-gray-700">
                <li>✓ Use keywords from the job description</li>
                <li>✓ Include specific technical skills and tools</li>
                <li>✓ Mention industry-standard terminology</li>
                <li>✓ Don't keyword stuff - keep it natural</li>
                <li>✓ List skills in Skills section prominently</li>
                <li>✓ Use the same terminology as job posting</li>
              </ul>
            </div>

            {/* Content Tips */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-3 text-purple-600">
                📝 Content Quality
              </h3>
              <ul className="space-y-2 text-gray-700">
                <li>✓ Use action verbs (managed, developed, implemented)</li>
                <li>✓ Quantify achievements with metrics</li>
                <li>✓ Tailor to each job position</li>
                <li>✓ Use consistent date formats</li>
                <li>✓ Keep descriptions concise and relevant</li>
                <li>✓ Focus on impact and results</li>
              </ul>
            </div>

            {/* Structure Tips */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-3 text-orange-600">
                🏗️ Resume Structure
              </h3>
              <ul className="space-y-2 text-gray-700">
                <li>✓ Keep to 1-2 pages (max 3 for experienced professionals)</li>
                <li>✓ Include all major sections needed for the role</li>
                <li>✓ Order sections by relevance to the job</li>
                <li>✓ Use bullet points for readability</li>
                <li>✓ Include phone number and email prominently</li>
                <li>✓ Link to portfolio or LinkedIn if relevant</li>
              </ul>
            </div>
          </div>
        </div>

        {/* ATS Score Scale */}
        <div className="mt-8 bg-white rounded-lg shadow p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Understanding Your ATS Score</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {[
              { grade: 'A', range: '90-100', color: 'bg-green-600', description: 'Excellent - High likelihood of passing ATS' },
              { grade: 'B', range: '80-89', color: 'bg-blue-600', description: 'Good - Well-optimized resume' },
              { grade: 'C', range: '70-79', color: 'bg-yellow-600', description: 'Fair - Some improvements needed' },
              { grade: 'D', range: '60-69', color: 'bg-orange-600', description: 'Poor - May not pass ATS' },
              { grade: 'F', range: '0-59', color: 'bg-red-600', description: 'Critical - Significant work needed' },
            ].map((item) => (
              <div key={item.grade} className="text-center">
                <div className={`${item.color} text-white rounded-lg p-4 mb-3`}>
                  <div className="text-3xl font-bold mb-1">{item.grade}</div>
                  <div className="text-sm">{item.range}</div>
                </div>
                <p className="text-sm text-gray-600">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
