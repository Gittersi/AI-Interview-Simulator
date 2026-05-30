import apiClient from './apiClient';

export const speechService = {
  startRecording: async (): Promise<MediaRecorder> => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    return new MediaRecorder(stream);
  },

  stopRecording: (recorder: MediaRecorder): Promise<Blob> => {
    return new Promise((resolve) => {
      recorder.ondataavailable = (event) => resolve(event.data);
      recorder.stop();
    });
  },

  transcribeAudio: async (blob: Blob): Promise<string> => {
    const formData = new FormData();
    formData.append('file', blob, 'answer.webm');

    const response = await apiClient.post<{ text: string }>('/speech/transcribe', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    return response.data.text;
  },

  checkRecordingPermission: async (): Promise<boolean> => {
    try {
      const permission = await navigator.permissions.query({
        name: 'microphone' as PermissionName,
      });
      return permission.state === 'granted';
    } catch {
      return false;
    }
  },
};
