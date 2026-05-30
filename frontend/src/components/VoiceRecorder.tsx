import React, { useState, useRef } from 'react';
import { Mic, MicOff } from 'lucide-react';
import { speechService } from '../services/speechService';

interface VoiceRecorderProps {
  onTranscription: (text: string) => void;
  disabled?: boolean;
}

export const VoiceRecorder: React.FC<VoiceRecorderProps> = ({
  onTranscription,
  disabled = false,
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const recorderRef = useRef<MediaRecorder | null>(null);

  const startRecording = async () => {
    try {
      const recorder = await speechService.startRecording();
      recorderRef.current = recorder;

      recorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Failed to start recording:', error);
      alert('Microphone access denied. Please enable microphone permissions.');
    }
  };

  const stopRecording = async () => {
    if (!recorderRef.current) return;

    setIsRecording(false);
    setIsTranscribing(true);

    const audioBlob = await speechService.stopRecording(recorderRef.current);

    try {
      const text = await speechService.transcribeAudio(audioBlob);
      onTranscription(text);
    } catch (error) {
      console.error('Transcription failed:', error);
      alert('Failed to transcribe audio. Please try again.');
    } finally {
      setIsTranscribing(false);
    }
  };

  return (
    <div className="flex items-center gap-4 p-4 bg-gray-100 rounded-lg">
      <button
        onClick={isRecording ? stopRecording : startRecording}
        disabled={disabled || isTranscribing}
        className={`p-3 rounded-full transition-all ${
          isRecording
            ? 'bg-red-500 hover:bg-red-600 text-white'
            : 'bg-blue-500 hover:bg-blue-600 text-white disabled:bg-gray-400'
        }`}
      >
        {isRecording ? (
          <MicOff className="w-6 h-6" />
        ) : (
          <Mic className="w-6 h-6" />
        )}
      </button>
      <div className="flex-1">
        {isRecording && (
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-600">Recording...</span>
          </div>
        )}
        {isTranscribing && (
          <span className="text-sm text-gray-600">Transcribing...</span>
        )}
        {!isRecording && !isTranscribing && (
          <span className="text-sm text-gray-600">
            {disabled ? 'Recording disabled' : 'Click to record your answer'}
          </span>
        )}
      </div>
    </div>
  );
};
