import React, { useState } from 'react';

interface CodingEditorProps {
  language: string;
  onExecute: (code: string) => Promise<void>;
  initialCode?: string;
}

export const CodingEditor: React.FC<CodingEditorProps> = ({
  language,
  onExecute,
  initialCode = '',
}) => {
  const [code, setCode] = useState(initialCode);
  const [isExecuting, setIsExecuting] = useState(false);
  const [output, setOutput] = useState('');

  const handleExecute = async () => {
    setIsExecuting(true);
    try {
      await onExecute(code);
      setOutput('Code executed successfully');
    } catch (error) {
      setOutput(`Error: ${error}`);
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <div className="flex flex-col gap-4 p-6 bg-white rounded-lg shadow-lg">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Code Editor</h3>
        <span className="px-3 py-1 bg-gray-200 rounded text-sm font-medium">
          {language}
        </span>
      </div>

      <textarea
        value={code}
        onChange={(e) => setCode(e.target.value)}
        placeholder={`Write your ${language} code here...`}
        className="w-full h-96 p-4 font-mono bg-gray-900 text-green-400 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 resize-none"
      />

      <button
        onClick={handleExecute}
        disabled={isExecuting || !code.trim()}
        className="w-full py-2 bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white font-semibold rounded-lg transition-all"
      >
        {isExecuting ? 'Executing...' : 'Execute Code'}
      </button>

      {output && (
        <div className="p-4 bg-gray-900 text-green-400 rounded-lg font-mono text-sm max-h-32 overflow-y-auto">
          {output}
        </div>
      )}
    </div>
  );
};
