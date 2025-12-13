import React, { useEffect, useState, useId } from 'react';
import './SemiCircularGauge.css';

/**
 * Semi-circular gauge component for displaying skin analysis scores
 * Displays score 0-100 with level indicators I-V
 */
export default function SemiCircularGauge({ score, label, animated = true }) {
    const [displayScore, setDisplayScore] = useState(0);
    const clipId = useId(); // Unique ID for each gauge instance

    // Get level from score (I-V)
    const getLevel = (s) => {
        if (s >= 80) return { level: 'I', desc: 'Sangat Baik' };
        if (s >= 60) return { level: 'II', desc: 'Baik' };
        if (s >= 40) return { level: 'III', desc: 'Sedang' };
        if (s >= 20) return { level: 'IV', desc: 'Perlu Perhatian' };
        return { level: 'V', desc: 'Kritis' };
    };

    // Animate score on mount
    useEffect(() => {
        if (!animated) {
            setDisplayScore(score);
            return;
        }

        const duration = 1500;
        const steps = 60;
        const increment = score / steps;
        let current = 0;
        let step = 0;

        const timer = setInterval(() => {
            step++;
            current = Math.min(score, increment * step);
            setDisplayScore(Math.round(current));

            if (step >= steps) {
                clearInterval(timer);
                setDisplayScore(score);
            }
        }, duration / steps);

        return () => clearInterval(timer);
    }, [score, animated]);

    const { level, desc } = getLevel(score);

    // Calculate arc path for filled portion
    const getArcPath = (percentage) => {
        const radius = 120;
        const centerX = 150;
        const centerY = 140;
        const startAngle = -180;
        const endAngle = startAngle + (percentage / 100) * 180;

        const startRad = (startAngle * Math.PI) / 180;
        const endRad = (endAngle * Math.PI) / 180;

        const startX = centerX + radius * Math.cos(startRad);
        const startY = centerY + radius * Math.sin(startRad);
        const endX = centerX + radius * Math.cos(endRad);
        const endY = centerY + radius * Math.sin(endRad);

        const largeArc = percentage > 50 ? 1 : 0;

        return `M ${startX} ${startY} A ${radius} ${radius} 0 ${largeArc} 1 ${endX} ${endY}`;
    };

    // Get color based on level
    const getColor = () => {
        if (score >= 80) return '#10b981'; // Green
        if (score >= 60) return '#22c55e'; // Light green
        if (score >= 40) return '#eab308'; // Yellow
        if (score >= 20) return '#f97316'; // Orange
        return '#ef4444'; // Red
    };

    // ClipPath for constraining the filled arc within track bounds
    // Semi-annulus shape: outer radius 132, inner radius 108 (120 ± 12)
    // FIXED: sweep-flag 0 for outer (counter-clockwise = UP), 1 for inner (clockwise = UP from right)
    const clipPathD = "M 18 140 A 132 132 0 0 0 282 140 L 258 140 A 108 108 0 0 1 42 140 Z";

    return (
        <div className="gauge-container">
            <svg viewBox="0 0 300 180" className="gauge-svg">
                {/* Define clipPath to constrain filled arc - unique ID per instance */}
                <defs>
                    <clipPath id={`gauge-clip-${clipId}`}>
                        <path d={clipPathD} />
                    </clipPath>
                </defs>

                {/* Background track */}
                <path
                    d="M 30 140 A 120 120 0 0 1 270 140"
                    fill="none"
                    stroke="rgba(255, 255, 255, 0.1)"
                    strokeWidth="24"
                    strokeLinecap="butt"
                />

                {/* Colored filled arc - clipped to track bounds */}
                <path
                    d={getArcPath(displayScore)}
                    fill="none"
                    stroke={getColor()}
                    strokeWidth="24"
                    strokeLinecap="butt"
                    clipPath={`url(#gauge-clip-${clipId})`}
                />

                {/* Scale marks */}
                {[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100].map((mark) => {
                    const angle = -180 + (mark / 100) * 180;
                    const rad = (angle * Math.PI) / 180;
                    const innerR = 95;
                    const outerR = 105;
                    const textR = 80;
                    const x1 = 150 + innerR * Math.cos(rad);
                    const y1 = 140 + innerR * Math.sin(rad);
                    const x2 = 150 + outerR * Math.cos(rad);
                    const y2 = 140 + outerR * Math.sin(rad);
                    const textX = 150 + textR * Math.cos(rad);
                    const textY = 140 + textR * Math.sin(rad);

                    return (
                        <g key={mark}>
                            <line
                                x1={x1}
                                y1={y1}
                                x2={x2}
                                y2={y2}
                                stroke="rgba(255, 255, 255, 0.4)"
                                strokeWidth={mark % 50 === 0 ? 2 : 1}
                            />
                            {mark % 20 === 0 && (
                                <text
                                    x={textX}
                                    y={textY}
                                    textAnchor="middle"
                                    dominantBaseline="middle"
                                    fill="rgba(255, 255, 255, 0.6)"
                                    fontSize="10"
                                >
                                    {mark}
                                </text>
                            )}
                        </g>
                    );
                })}

                {/* Level indicators (I-V) on outer arc */}
                {['I', 'II', 'III', 'IV', 'V'].map((lvl, i) => {
                    // Position levels around the arc (V at left, I at right)
                    const positions = [170, 135, 90, 45, 10]; // Percentages
                    const angle = -180 + (positions[i] / 100) * 180;
                    const rad = (angle * Math.PI) / 180;
                    const r = 155;
                    const x = 150 + r * Math.cos(rad);
                    const y = 140 + r * Math.sin(rad);

                    return (
                        <text
                            key={lvl}
                            x={x}
                            y={y}
                            textAnchor="middle"
                            dominantBaseline="middle"
                            fill={level === lvl ? '#00d4ff' : 'rgba(255, 255, 255, 0.4)'}
                            fontSize={level === lvl ? '16' : '12'}
                            fontWeight={level === lvl ? 'bold' : 'normal'}
                        >
                            {lvl}
                        </text>
                    );
                })}

                {/* Center display */}
                <text
                    x="150"
                    y="110"
                    textAnchor="middle"
                    fill="#ffffff"
                    fontSize="48"
                    fontWeight="bold"
                    className="gauge-score"
                >
                    {level}
                </text>

                {/* Label */}
                <text
                    x="150"
                    y="150"
                    textAnchor="middle"
                    fill="rgba(255, 255, 255, 0.8)"
                    fontSize="14"
                    fontWeight="500"
                >
                    {label}
                </text>
            </svg>

            {/* Score display below */}
            <div className="gauge-score-display">
                <span className="gauge-score-value" style={{ color: getColor() }}>
                    {displayScore}
                </span>
                <span className="gauge-score-max">/100</span>
            </div>

            <div className="gauge-level-desc">{desc}</div>
        </div>
    );
}
