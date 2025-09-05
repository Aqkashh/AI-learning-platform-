const express = require('express');
const axios = require('axios');
const cors = require('cors');
const multer = require('multer');
const FormData = require('form-data');

const app = express();
const upload = multer();
const PORT = process.env.PORT || 5000;
const FASTAPI_URL = process.env.FASTAPI_URL || 'http://127.0.0.1:8000';

app.use(cors());

// Web-based summarization 
app.post('/api/process-topic', express.json(), async (req, res) => {
    try {
        const { topic } = req.body;
        const response = await axios.post(`${FASTAPI_URL}/summarize-web`, { topic });
        res.json(response.data);
    } catch (error) {
        console.error('Error forwarding request to FastAPI:', error.message);
        res.status(500).json({ error: 'Failed to process request.' });
    }
});

// PDF summarization 
app.post('/api/process-pdf', upload.single('file'), async (req, res) => {
    try {
        const form = new FormData();
        form.append('file', req.file.buffer, { filename: req.file.originalname, contentType: req.file.mimetype });

        const response = await axios.post(`${FASTAPI_URL}/summarize-pdf`, form, {
            headers: form.getHeaders(),
        });

        res.json(response.data);
    } catch (error) {
        console.error('Error forwarding request to FastAPI:', error.message);
        res.status(500).json({ error: 'Failed to process request.' });
    }
});

// Combined summarization 
app.post('/api/process-combined', upload.single('file'), async (req, res) => {
    try {
        const form = new FormData();
        form.append('topic', req.body.topic);
        form.append('file', req.file.buffer, { filename: req.file.originalname, contentType: req.file.mimetype });

        const response = await axios.post(`${FASTAPI_URL}/summarize-combined`, form, {
            headers: form.getHeaders(),
        });

        res.json(response.data);
    } catch (error) {
        console.error('Error forwarding request to FastAPI:', error.message);
        res.status(500).json({ error: 'Failed to process request.' });
    }
});

// Quiz generation (handles JSON body)
app.post('/api/generate-quiz', express.json(), async (req, res) => {
    try {
        const { summary } = req.body;
        const response = await axios.post(`${FASTAPI_URL}/generate-quiz`, { summary }, {
            headers: {
                'Content-Type': 'application/json'
            }
        });
        res.json(response.data);
    } catch (error) {
        console.error('Error forwarding request to FastAPI:', error.message);
        res.status(500).json({ error: 'Failed to process request.' });
    }
});
app.listen(PORT, () => {
    console.log(`Node.js API Gateway listening on port ${PORT}`);
});