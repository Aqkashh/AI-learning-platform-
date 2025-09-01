// frontend/src/App.js
import { useState } from 'react';
import axios from 'axios';
import './App.css'; // Assuming you have some basic styles

function App() {
  const [topic, setTopic] = useState('');
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSummarize = async () => {
    setLoading(true);
    setError('');
    setSummary('');

    try {
      // Make a POST request to your Node.js API gateway
      const response = await axios.post('http://localhost:5000/api/process-topic', {
        topic: topic
      });

      // Update the state with the summary from the backend
      setSummary(response.data.summary);

    } catch (err) {
      console.error(err);
      setError('Failed to fetch summary. Please check your backend servers.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI-Powered Summarizer</h1>
        <p>Enter a topic below and get an AI-generated summary.</p>

        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="e.g., Quantum Computing"
        />

        <button onClick={handleSummarize} disabled={!topic || loading}>
          {loading ? 'Summarizing...' : 'Get Summary'}
        </button>

        {error && <p className="error-message">{error}</p>}
        
        {summary && (
          <div className="summary-container">
            <h2>Summary:</h2>
            <p>{summary}</p>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;