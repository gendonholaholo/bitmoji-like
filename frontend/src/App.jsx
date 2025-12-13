import React, { useState } from 'react';
import UploadSection from './components/UploadSection';
import ResultsDashboard from './components/ResultsDashboard';
import { uploadImage, pollResult, isMockMode } from './services/api';
import './App.css';

function App() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState({ current: 0, total: 720 });

  const handleImageUpload = async (file) => {
    setIsProcessing(true);
    setError(null);
    setResults(null);

    try {
      // Step 1: Upload image and get task_id
      console.log('Uploading image...');
      const uploadResponse = await uploadImage(file);
      const taskId = uploadResponse.task_id;

      console.log('Task ID:', taskId);

      // Step 2: Poll for results
      console.log('Polling for results...');
      const result = await pollResult(
        taskId,
        (status, attempt, maxAttempts) => {
          setProgress({ current: attempt + 1, total: maxAttempts });
          console.log(`Status: ${status}, Attempt: ${attempt + 1}/${maxAttempts}`);
        }
      );

      console.log('Analysis complete!', result);
      setResults(result);
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.message || 'Analysis failed. Please try again.');
    } finally {
      setIsProcessing(false);
      setProgress({ current: 0, total: 720 });
    }
  };

  const handleReset = () => {
    setResults(null);
    setError(null);
    setIsProcessing(false);
  };

  return (
    <div className="app">
      {/* Mock Mode Indicator */}
      {isMockMode() && (
        <div className="mock-mode-badge">
          📦 MOCK MODE
        </div>
      )}
      
      {!results ? (
        <>
          <UploadSection
            onImageUpload={handleImageUpload}
            isProcessing={isProcessing}
          />

          {isProcessing && (
            <div className="progress-info">
              <p>
                Analyzing... ({progress.current}/{progress.total})
              </p>
              <p className="progress-tip">
                This may take up to 1 hour
              </p>
            </div>
          )}

          {error && (
            <div className="error-banner">
              <p>{error}</p>
              <button className="btn btn-primary" onClick={handleReset}>
                Try Again
              </button>
            </div>
          )}
        </>
      ) : (
        <>
          <ResultsDashboard results={results} />

          <div className="reset-section">
            <button className="btn btn-primary" onClick={handleReset}>
              Analyze Another Image
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default App;
