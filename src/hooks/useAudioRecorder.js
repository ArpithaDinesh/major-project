import { useState, useRef, useEffect } from 'react';

export const useAudioRecorder = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioUrl, setAudioUrl] = useState(null);
  const [audioBlob, setAudioBlob] = useState(null);
  const [waveformData, setWaveformData] = useState(new Array(24).fill(15));

  const timerRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const animFrameRef = useRef(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    };
  }, []);

  const startRecording = async () => {
    setAudioUrl(null);
    setAudioBlob(null);
    setRecordingTime(0);
    audioChunksRef.current = [];

    // Simulate animated waveform bars while recording
    const updateWaveform = () => {
      setWaveformData(
        Array.from({ length: 24 }, () => Math.floor(Math.random() * 75) + 15)
      );
      animFrameRef.current = requestAnimationFrame(() => {
        setTimeout(updateWaveform, 120);
      });
    };

    try {
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data);
          }
        };

        mediaRecorder.onstop = () => {
          const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          const url = URL.createObjectURL(blob);
          setAudioBlob(blob);
          setAudioUrl(url);
          stream.getTracks().forEach((track) => track.stop());
        };

        mediaRecorder.start(100);
      }
    } catch (err) {
      console.warn("Real microphone access not available, running simulated recorder:", err);
    }

    setIsRecording(true);
    updateWaveform();

    timerRef.current = setInterval(() => {
      setRecordingTime((prev) => prev + 1);
    }, 1000);
  };

  const stopRecording = () => {
    if (!isRecording) return;
    setIsRecording(false);
    clearInterval(timerRef.current);
    if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);

    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    } else {
      // Create mock audio fallback
      setAudioUrl('mock-audio-captured');
    }
  };

  const resetRecording = () => {
    setIsRecording(false);
    setRecordingTime(0);
    setAudioUrl(null);
    setAudioBlob(null);
    setWaveformData(new Array(24).fill(15));
    if (timerRef.current) clearInterval(timerRef.current);
    if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return {
    isRecording,
    recordingTime,
    formattedTime: formatTime(recordingTime),
    audioUrl,
    audioBlob,
    waveformData,
    startRecording,
    stopRecording,
    resetRecording,
  };
};
