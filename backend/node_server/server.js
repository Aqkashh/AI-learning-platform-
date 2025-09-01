// server.js
const express = require('express');
const axios = require('axios');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 5000;
const FASTAPI_URL = process.env.FASTAPI_URL || 'http://127.0.0.1:8000';

// Middleware to parse JSON bodies
app.use(express.json());

// Enable CORS for all routes
// This allows your React app (on a different port) to make requests
app.use(cors());

// Main API gateway endpoint
// It will forward the request to the FastAPI service
app.post('/api/process-topic', async (req, res) => {
    try {
        const { topic } = req.body;

        // Make a POST request to the FastAPI service
        const response = await axios.post(`${FASTAPI_URL}/summarize-web`, {
            topic: topic
        });

        // Forward the response from FastAPI back to the frontend
        res.json(response.data);
    } catch (error) {
        console.error('Error forwarding request to FastAPI:', error.message);
        res.status(500).json({ error: 'Failed to process request.' });
    }
});

// Start the server
app.listen(PORT, () => {
    console.log(`Node.js API Gateway listening on port ${PORT}`);
});