import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

// Upload image and start analysis
export async function uploadImage(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post(`${API_BASE_URL}/analyze`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });

    return response.data;
}

// Poll for analysis results
export async function getResult(taskId) {
    const response = await axios.get(`${API_BASE_URL}/result/${taskId}`);
    return response.data;
}

// Poll result until completed (max 1 hour timeout as requested)
export async function pollResult(taskId, onProgress, maxAttempts = 720, interval = 5000) {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
        try {
            const result = await getResult(taskId);

            if (onProgress) {
                onProgress(result.status, attempt, maxAttempts);
            }

            if (result.status === 'completed') {
                return result;
            }

            if (result.status === 'failed') {
                throw new Error(result.error_message || result.error || 'Analysis failed');
            }

            // Wait before next poll
            await new Promise(resolve => setTimeout(resolve, interval));
        } catch (error) {
            // If it's the last attempt, throw the error
            if (attempt === maxAttempts - 1) {
                throw error;
            }
            // Otherwise, continue polling
            await new Promise(resolve => setTimeout(resolve, interval));
        }
    }

    throw new Error('Analysis timeout - please try again');
}
