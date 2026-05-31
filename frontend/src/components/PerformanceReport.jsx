import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export const PerformanceReport = ({ report }) => {
  const scoreData = [
    { name: 'Correctness', value: report.correctnessScore },
    { name: 'Communication', value: report.communicationScore },
    { name: 'Confidence', value: report.confidenceScore },
  ];

  return (
    <div className="space-y-6 p-6 bg-white rounded-lg shadow-lg">
      <div>
        <h2 className="text-2xl font-bold mb-4">Performance Report</h2>
        <div className="grid grid-cols-3 gap-4">
          <div className="p-4 bg-blue-50 rounded-lg">
            <p className="text-gray-600 text-sm">Total Score</p>
            <p className="text-3xl font-bold text-blue-600">
              {report.totalScore.toFixed(1)}%
            </p>
          </div>
          <div className="p-4 bg-green-50 rounded-lg">
            <p className="text-gray-600 text-sm">Correctness</p>
            <p className="text-3xl font-bold text-green-600">
              {report.correctnessScore.toFixed(1)}%
            </p>
          </div>
          <div className="p-4 bg-purple-50 rounded-lg">
            <p className="text-gray-600 text-sm">Communication</p>
            <p className="text-3xl font-bold text-purple-600">
              {report.communicationScore.toFixed(1)}%
            </p>
          </div>
        </div>
      </div>

      <div className="h-80">
        <h3 className="text-lg font-semibold mb-4">Score Breakdown</h3>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={scoreData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="value" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-4">Feedback</h3>
        <div className="space-y-3">
          {report.suggestions.map((suggestion, index) => (
            <div key={index} className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-gray-700">{suggestion}</p>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-4">Detailed Evaluations</h3>
        <div className="space-y-3">
          {report.evaluations.map((evaluation) => (
            <div key={evaluation.answerId} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
              <div className="flex justify-between mb-2">
                <p className="font-medium">Question {evaluation.answerId}</p>
                <div className="flex gap-2">
                  <span className="text-sm px-2 py-1 bg-green-100 text-green-700 rounded">
                    Correctness: {evaluation.correctness}%
                  </span>
                  <span className="text-sm px-2 py-1 bg-blue-100 text-blue-700 rounded">
                    Confidence: {evaluation.confidence}%
                  </span>
                </div>
              </div>
              <p className="text-gray-700 text-sm">{evaluation.feedback}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
