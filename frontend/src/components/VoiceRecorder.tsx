import React, { useState, useRef } from 'react';
import { Mic, MicOff, AlertCircle } from 'lucide-react';
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
  const [error, setError] = useState<string | null>(null);
  const [errorType, setErrorType] = useState<'permission' | 'transcription' | 'recording' | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const recordingTimeRef = useRef<number>(0);
  const recordingTimerRef = useRef<NodeJS.Timeout | null>(null);

  const clearError = () => {
    setError(null);
    setErrorType(null);
  };

  const startRecording = async () => {
    try {
      clearError();
      
      // Check for browser support
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Your browser does not support audio recording');
      }
      
      const recorder = await speechService.startRecording();
      recorderRef.current = recorder;

      recordingTimeRef.current = 0;
      recordingTimerRef.current = setInterval(() => {
        recordingTimeRef.current += 1;
        // Warn if recording is too long (> 5 minutes)
        if (recordingTimeRef.current > 300) {
          setError('Recording is too long. Please submit your answer.');
        }
      }, 1000);

      recorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Failed to start recording:', error);
      
      if (error instanceof Error) {
        if (error.message.includes('NotAllowedError') || error.message.includes('Permission denied')) {
          setErrorType('permission');
          setError('Microphone access denied. Please enable microphone permissions in your browser settings.');
        } else if (error.message.includes('NotFoundError')) {
          setErrorType('recording');
          setError('No microphone found. Please connect a microphone and try again.');
        } else if (error.message.includes('NotSupportedError')) {
          setErrorType('recording');
          setError('Audio recording is not supported in your browser.');
        } else {
          setErrorType('recording');
          setError(`Recording failed: ${error.message}`);
        }
      } else {
        setErrorType('recording');
        setError('Failed to start recording. Please check your microphone settings.');
      }
    }
  };

  const stopRecording = async () => {
    if (!recorderRef.current) return;

    setIsRecording(false);
    
    // Clear the timer
    if (recordingTimerRef.current) {
      clearInterval(recordingTimerRef.current);
      recordingTimerRef.current = null;
    }

    setIsTranscribing(true);
    clearError();

    try {
      const audioBlob = await speechService.stopRecording(recorderRef.current);
      console.log(`Audio recorded: ${audioBlob.size} bytes, ${recordingTimeRef.current}s duration`);

      if (audioBlob.size === 0) {
        throw new Error('No audio was recorded. Please try again.');
      }

      const text = await speechService.transcribeAudio(audioBlob);
      onTranscription(text);
    } catch (error) {
      console.error('Transcription failed:', error);
      
      if (error instanceof Error) {
        if (error.message.includes('timeout') || error.message.includes('504')) {
          setErrorType('transcription');
          setError('Transcription service is taking too long. Please try again.');
        } else if (error.message.includes('502')) {
          setErrorType('transcription');
          setError('Transcription service is unavailable. Please try again later.');
        } else if (error.message.includes('413') || error.message.includes('too large')) {
          setErrorType('transcription');
          setError('Audio file is too large. Please record a shorter answer.');
        } else if (error.message.includes('400') || error.message.includes('empty')) {
          setErrorType('recording');
          setError('Recording is empty or invalid. Please try again.');
        } else {
          setErrorType('transcription');
          setError(`Transcription failed: ${error.message}`);
        }
      } else {
        setErrorType('transcription');
        setError('Transcription failed. Please try again.');
      }
    } finally {
      setIsTranscribing(false);
    }
  };

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-4 p-4 bg-gray-100 rounded-lg">
        <button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={disabled || isTranscribing}
          className={`p-3 rounded-full transition-all flex-shrink-0 ${
            isRecording
              ? 'bg-red-500 hover:bg-red-600 text-white'
              : 'bg-blue-500 hover:bg-blue-600 text-white disabled:bg-gray-400'
          }`}
          title={isRecording ? 'Stop recording' : 'Start recording'}
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
              <span className="text-sm text-gray-600">
                Recording... {Math.floor(recordingTimeRef.current / 60)}:{String(recordingTimeRef.current % 60).padStart(2, '0')}
              </span>
            </div>
          )}
          {isTranscribing && (
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-600">Processing audio...</span>
            </div>
          )}
          {!isRecording && !isTranscribing && (
            <span className="text-sm text-gray-600">
              {disabled ? 'Recording disabled' : 'Click to record your answer'}
            </span>
          )}
        </div>
      </div>

      {error && (
        <div className={`flex items-start gap-3 p-3 rounded-lg border ${
          errorType === 'permission'
            ? 'bg-orange-50 border-orange-200 text-orange-800'
            : errorType === 'transcription'
            ? 'bg-red-50 border-red-200 text-red-800'
            : 'bg-yellow-50 border-yellow-200 text-yellow-800'
        }`}>
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm font-medium">{error}</p>
            {errorType === 'permission' && (
              <p className="text-xs mt-1 opacity-75">
                Go to your browser settings and allow microphone access for this site
              </p>
            )}
            {errorType === 'transcription' && (
              <p className="text-xs mt-1 opacity-75">
                Check your internet connection and try again
              </p>
            )}
          </div>
          <button
            onClick={clearError}
            className="text-xs font-medium opacity-75 hover:opacity-100 flex-shrink-0"
          >
            Dismiss
          </button>
        </div>
      )}
    </div>
  );
};
