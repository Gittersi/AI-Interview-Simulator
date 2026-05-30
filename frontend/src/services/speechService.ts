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
    // This would use AssemblyAI or another speech-to-text API
    // For now, returning placeholder
    const apiKey = import.meta.env.VITE_SPEECH_API_KEY;
    const formData = new FormData();
    formData.append('file', blob);

    try {
      const response = await fetch('https://api.assemblyai.com/v2/upload', {
        method: 'POST',
        headers: {
          Authorization: apiKey,
        },
        body: formData,
      });

      const uploadUrl = (await response.json()).upload_url;

      const transcriptResponse = await fetch('https://api.assemblyai.com/v2/transcript', {
        method: 'POST',
        headers: {
          Authorization: apiKey,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ audio_url: uploadUrl }),
      });

      const transcript = await transcriptResponse.json();
      return transcript.text || '';
    } catch (error) {
      console.error('Transcription error:', error);
      return '';
    }
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
