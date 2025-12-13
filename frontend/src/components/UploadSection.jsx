import React, { useState } from 'react';
import { Upload, Loader2, AlertCircle } from 'lucide-react';
import './UploadSection.css';

export default function UploadSection({ onImageUpload, isProcessing }) {
    const [dragActive, setDragActive] = useState(false);
    const [preview, setPreview] = useState(null);
    const [error, setError] = useState(null);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        const file = e.dataTransfer.files?.[0];
        if (file) {
            handleFile(file);
        }
    };

    const handleChange = (e) => {
        const file = e.target.files?.[0];
        if (file) {
            handleFile(file);
        }
    };

    const handleFile = (file) => {
        setError(null);

        // Validate file type
        if (!file.type.startsWith('image/')) {
            setError('Please upload an image file');
            return;
        }

        // Validate file size (10MB max)
        if (file.size > 10 * 1024 * 1024) {
            setError('File size must be less than 10MB');
            return;
        }

        // Create preview
        const reader = new FileReader();
        reader.onload = (e) => {
            setPreview(e.target.result);
        };
        reader.readAsDataURL(file);

        // Upload file
        onImageUpload(file);
    };

    return (
        <div className="upload-section fade-in">
            <div className="upload-header">
                <h1>AI Skin Analysis</h1>
                <p>Take a selfie for comprehensive skin analysis</p>
            </div>

            <div
                className={`upload-zone ${dragActive ? 'drag-active' : ''} ${preview ? 'has-preview' : ''}`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
            >
                {preview ? (
                    <div className="preview-container">
                        <img src={preview} alt="Preview" className="preview-image" />
                        {isProcessing && (
                            <div className="processing-overlay">
                                <Loader2 className="spinner" size={48} />
                                <p>Analyzing your skin...</p>
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="upload-placeholder">
                        <Upload size={64} className="upload-icon" />
                        <h3>Drag & drop your selfie here</h3>
                        <p>or click to browse</p>
                        <p className="upload-hint">Supports: JPG, PNG (Max 10MB)</p>
                    </div>
                )}

                <input
                    type="file"
                    id="file-upload"
                    className="file-input"
                    accept="image/*"
                    onChange={handleChange}
                    disabled={isProcessing}
                />
            </div>

            {error && (
                <div className="error-message">
                    <AlertCircle size={20} />
                    <span>{error}</span>
                </div>
            )}
        </div>
    );
}
