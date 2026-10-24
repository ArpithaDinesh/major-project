import React from 'react';

export const AudioWaveform = ({ waveformData = [], isRecording = false }) => {
  return (
    <div className="flex items-center justify-center gap-1.5 h-16 w-full px-4 py-2 bg-dark-bg/80 rounded-xl border border-dark-border/60">
      {waveformData.map((height, i) => (
        <div
          key={i}
          className={`w-1 rounded-full transition-all duration-150 ${
            isRecording ? 'bg-gradient-to-t from-accent to-accent-teal' : 'bg-dark-border'
          }`}
          style={{
            height: isRecording ? `${Math.max(12, height)}%` : '15%',
            opacity: isRecording ? 0.9 : 0.4
          }}
        />
      ))}
    </div>
  );
};
