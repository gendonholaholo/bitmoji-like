import axios from 'axios';
import { 
    isMockMode, 
    getMockDelay, 
    delay, 
    mockUploadResponse, 
    generateMockResult 
} from './mockData';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

// Store uploaded file for mock mode
let _mockUploadedFile = null;

/**
 * Upload image and start analysis
 * In mock mode: stores file and returns fake task_id
 * In real mode: uploads to API
 */
export async function uploadImage(file) {
    // Check mock mode
    if (isMockMode()) {
        console.log('📦 [MOCK MODE] Simulating image upload...');
        _mockUploadedFile = file;
        await delay(getMockDelay() / 2); // Simulate upload delay
        return mockUploadResponse();
    }

    // Real API call
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post(`${API_BASE_URL}/analyze`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });

    return response.data;
}

/**
 * Get analysis results by task ID
 * In mock mode: returns generated mock data
 * In real mode: fetches from API
 */
export async function getResult(taskId) {
    // Check mock mode
    if (isMockMode()) {
        console.log('📦 [MOCK MODE] Generating mock result...');
        await delay(getMockDelay());
        const result = await generateMockResult(_mockUploadedFile);
        return result;
    }

    // Real API call
    const response = await axios.get(`${API_BASE_URL}/result/${taskId}`);
    return response.data;
}

/**
 * Poll result until completed
 * In mock mode: returns result immediately after delay
 * In real mode: polls API until status is 'completed' or 'failed'
 */
export async function pollResult(taskId, onProgress, maxAttempts = 720, interval = 5000) {
    // Check mock mode - simplified polling
    if (isMockMode()) {
        console.log('📦 [MOCK MODE] Starting mock polling...');
        
        // Simulate a few polling attempts for realism
        const mockAttempts = 3;
        for (let i = 0; i < mockAttempts; i++) {
            if (onProgress) {
                onProgress('processing', i, mockAttempts + 1);
            }
            await delay(getMockDelay() / mockAttempts);
        }
        
        // Final result
        if (onProgress) {
            onProgress('completed', mockAttempts, mockAttempts + 1);
        }
        
        const result = await generateMockResult(_mockUploadedFile);
        console.log('📦 [MOCK MODE] Mock analysis complete!');
        return result;
    }

    // Real API polling
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

/**
 * Check if currently in mock mode
 * Useful for UI indicators
 */
export { isMockMode };
