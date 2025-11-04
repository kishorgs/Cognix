const API_BASE_URL = 'http://localhost:5000/api';

const defaultHeaders = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
};

const handleResponse = async (response) => {
    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText);
    }
    return response.json();
};

export const apiService = {
    async processDocument(text, metadata) {
        // Change from port 5000 to 8000
        const response = await fetch('http://localhost:8000/api/process-document', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text, metadata }),
        });

        return handleResponse(response);
    },

    async searchDocuments(query, topK = 5) {
        const response = await fetch(`${API_BASE_URL}/search`, {
            method: 'POST',
            headers: defaultHeaders,
            mode: 'cors',
            body: JSON.stringify({ query, top_k: topK })
        });
        return handleResponse(response);
    }
};

export default apiService;