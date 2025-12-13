import React, { useState, useRef, useCallback } from 'react';
import './ImageComparisonSlider.css';

/**
 * Image comparison slider component
 * Allows users to compare two images by dragging a slider
 */
export default function ImageComparisonSlider({
    beforeImage,
    afterImage,
    beforeLabel = 'Sebelum',
    afterLabel = 'Sesudah',
}) {
    const [sliderPosition, setSliderPosition] = useState(50);
    const [isDragging, setIsDragging] = useState(false);
    const containerRef = useRef(null);

    const handleMove = useCallback((clientX) => {
        if (!containerRef.current) return;

        const rect = containerRef.current.getBoundingClientRect();
        const x = clientX - rect.left;
        const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100));
        setSliderPosition(percentage);
    }, []);

    const handleMouseDown = (e) => {
        e.preventDefault();
        setIsDragging(true);
        handleMove(e.clientX);
    };

    const handleMouseMove = useCallback((e) => {
        if (!isDragging) return;
        handleMove(e.clientX);
    }, [isDragging, handleMove]);

    const handleMouseUp = useCallback(() => {
        setIsDragging(false);
    }, []);

    const handleTouchStart = (e) => {
        setIsDragging(true);
        handleMove(e.touches[0].clientX);
    };

    const handleTouchMove = useCallback((e) => {
        if (!isDragging) return;
        handleMove(e.touches[0].clientX);
    }, [isDragging, handleMove]);

    const handleTouchEnd = useCallback(() => {
        setIsDragging(false);
    }, []);

    // Add/remove global event listeners for dragging
    React.useEffect(() => {
        if (isDragging) {
            document.addEventListener('mousemove', handleMouseMove);
            document.addEventListener('mouseup', handleMouseUp);
            document.addEventListener('touchmove', handleTouchMove);
            document.addEventListener('touchend', handleTouchEnd);
        }

        return () => {
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
            document.removeEventListener('touchmove', handleTouchMove);
            document.removeEventListener('touchend', handleTouchEnd);
        };
    }, [isDragging, handleMouseMove, handleMouseUp, handleTouchMove, handleTouchEnd]);

    return (
        <div
            ref={containerRef}
            className={`comparison-slider ${isDragging ? 'dragging' : ''}`}
            onMouseDown={handleMouseDown}
            onTouchStart={handleTouchStart}
        >
            {/* After image (full width background) */}
            <div className="comparison-image-container after-container">
                <img
                    src={afterImage}
                    alt={afterLabel}
                    className="comparison-image"
                    draggable={false}
                />
                <span className="comparison-label after-label">{afterLabel}</span>
            </div>

            {/* Before image (clipped by slider position) */}
            <div
                className="comparison-image-container before-container"
                style={{ clipPath: `inset(0 ${100 - sliderPosition}% 0 0)` }}
            >
                <img
                    src={beforeImage}
                    alt={beforeLabel}
                    className="comparison-image"
                    draggable={false}
                />
                <span className="comparison-label before-label">{beforeLabel}</span>
            </div>

            {/* Slider line and handle */}
            <div
                className="slider-line"
                style={{ left: `${sliderPosition}%` }}
            >
                <div className="slider-handle">
                    <div className="slider-handle-arrows">
                        <span className="arrow left">◀</span>
                        <span className="arrow right">▶</span>
                    </div>
                </div>
            </div>

            {/* Instruction text */}
            {!isDragging && (
                <div className="slider-instruction">
                    Geser untuk membandingkan
                </div>
            )}
        </div>
    );
}
