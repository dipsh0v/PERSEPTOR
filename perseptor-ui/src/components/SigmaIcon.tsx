import React from 'react';

interface SigmaIconProps {
  color?: string;
  width?: number;
  height?: number;
}

const SigmaIcon: React.FC<SigmaIconProps> = ({ color = 'inherit', width = 24, height = 24 }) => (
  <svg width={width} height={height} viewBox="0 0 24 24" fill="none">
    <path
      d="M17.5 18.5H7.5V16.5L12.5 12L7.5 7.5V5.5H17.5V8.5H11.5L15.5 12L11.5 15.5H17.5V18.5Z"
      fill={color}
    />
  </svg>
);

export default SigmaIcon; 