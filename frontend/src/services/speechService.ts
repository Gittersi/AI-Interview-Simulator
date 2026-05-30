import apiClient from './apiClient';

interface RecordingError {
  code: string;
  message: string;
}

export const speechService = {
  startRecording: async (): Promise<MediaRecorder> => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        }
      });
      
      if (!stream || !stream.active) {
        throw new Error('Failed to get active audio stream');
      }
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
          ? 'audio/webm;codecs=opus'
          : 'audio/webm',
      });
      
      return mediaRecorder;
    } catch (error) {
      if (error instanceof DOMException) {
        throw {
          code: error.name,
          message: error.message,
        } as RecordingError;
      }
      throw error;
    }
  },

  stopRecording: (recorder: MediaRecorder): Promise<Blob> => {
    return new Promise((resolve, reject) => {
      if (!recorder) {
        reject(new Error('No recorder available'));
        return;
      }
      
      const chunks: BlobPart[] = [];
      
      recorder.ondataavailable = (event: BlobEvent) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };
      
      recorder.onerror = (event: Event) => {
        if (event instanceof ErrorEvent) {
          reject(new Error(`Recording error: ${event.error}`));
        } else {
          reject(new Error('Recording error occurred'));
        }
      };
      
      recorder.onstop = () => {
        if (chunks.length === 0) {
          reject(new Error('No audio data recorded'));
          return;
        }
        const blob = new Blob(chunks, { type: recorder.mimeType || 'audio/webm' });
        resolve(blob);
      };
      
      recorder.stop();
      
      // Stop all tracks to release microphone
      recorder.stream.getTracks().forEach(track => track.stop());
    });
  },

  transcribeAudio: async (blob: Blob): Promise<string> => {
    try {
      if (!blob || blob.size === 0) {
        throw new Error('Audio blob is empty');
      }
      
      if (blob.size > 25 * 1024 * 1024) { // 25MB limit
        throw new Error('Audio file too large (max 25MB)');
      }
      
      const formData = new FormData();
      formData.append('file', blob, 'answer.webm');
      
      console.info(`Uploading audio: ${blob.size} bytes, type: ${blob.type}`);
      
      const response = await apiClient.post<{ text: string; status: string }>(
        '/speech/transcribe',
        formData
      );
      
      if (!response.data.text) {
        throw new Error('Server returned empty transcription');
      }
      
      console.info(`Transcription successful: ${response.data.text.length} characters`);
      return response.data.text;
    } catch (error) {
      if (error instanceof Error) {
        console.error(`Transcription failed: ${error.message}`);
        throw error;
      }
      throw new Error('Unknown transcription error');
    }
  },

  textToSpeech: async (text: string): Promise<void> => {
    try {
      if (!text || !text.trim()) {
        throw new Error('No text provided for speech synthesis');
      }
      
      if (!('speechSynthesis' in window)) {
        throw new Error('Speech synthesis not supported in this browser');
      }
      
      // Cancel any ongoing speech
      window.speechSynthesis.cancel();
      
      // Validate with backend
      await apiClient.post('/speech/text-to-speech', { text });
      
      // Use Web Speech API for local synthesis
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      utterance.volume = 1.0;
      
      return new Promise((resolve, reject) => {
        utterance.onend = () => {
          console.info('Speech synthesis ended');
          resolve();
        };
        
        utterance.onerror = (event: SpeechSynthesisErrorEvent) => {
          console.error(`Speech synthesis error: ${event.error}`);
          reject(new Error(`Speech synthesis error: ${event.error}`));
        };
        
        window.speechSynthesis.speak(utterance);
      });
    } catch (error) {
      if (error instanceof Error) {
        console.error(`Text-to-speech failed: ${error.message}`);
        throw error;
      }
      throw new Error('Unknown text-to-speech error');
    }
  },

  stopSpeech: (): void => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
  },

  checkRecordingPermission: async (): Promise<boolean> => {
    try {
      const permission = await navigator.permissions.query({
        name: 'microphone' as PermissionName,
      });
      return permission.state === 'granted';
    } catch {
      // If permissions API is not supported, assume we can try
      return true;
    }
  },

  checkSpeechSynthesisSupport: (): boolean => {
    return 'speechSynthesis' in window;
  },
};
