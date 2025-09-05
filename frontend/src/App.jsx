import { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [topic, setTopic] = useState('');
  const [summary, setSummary] = useState('');
  const [quiz, setQuiz] = useState(null);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('web'); // 'web', 'pdf', 'combined'

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSummarize = async () => {
    setLoading(true);
    setError('');
    setSummary('');
    setQuiz(null);

    try {
      let response;
      if (activeTab === 'web') {
        response = await axios.post('http://localhost:5000/api/process-topic', { topic });
      } else if (activeTab === 'pdf') {
        const formData = new FormData();
        formData.append('file', file);
        response = await axios.post('http://localhost:5000/api/process-pdf', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      } else if (activeTab === 'combined') {
        const formData = new FormData();
        formData.append('topic', topic);
        formData.append('file', file);
        response = await axios.post('http://localhost:5000/api/process-combined', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      }
      setSummary(response.data.summary);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch summary. Check your backend servers.');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateQuiz = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.post('http://localhost:5000/api/generate-quiz', { summary });
      setQuiz(response.data);
    } catch (err) {
      console.error(err);
      setError('Failed to generate quiz.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI-Powered Summarizer & Quiz Generator</h1>
        <p>Get a summary and a multiple-choice quiz from web data or a PDF.</p>

        <div className="tabs">
          <button onClick={() => setActiveTab('web')} className={activeTab === 'web' ? 'active' : ''}>
            Web Summary
          </button>
          <button onClick={() => setActiveTab('pdf')} className={activeTab === 'pdf' ? 'active' : ''}>
            PDF Summary
          </button>
          <button onClick={() => setActiveTab('combined')} className={activeTab === 'combined' ? 'active' : ''}>
            Combined
          </button>
        </div>

        <div className="input-container">
          {(activeTab === 'web' || activeTab === 'combined') && (
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Enter a topic..."
            />
          )}
          {(activeTab === 'pdf' || activeTab === 'combined') && (
            <input type="file" onChange={handleFileChange} />
          )}
          <button onClick={handleSummarize} disabled={loading || (!topic && activeTab !== 'pdf') || (activeTab !== 'web' && !file)}>
            {loading ? 'Processing...' : 'Get Summary'}
          </button>
        </div>

        {error && <p className="error-message">{error}</p>}
        
        {summary && (
          <div className="summary-container">
            <h2>Summary:</h2>
            <p>{summary}</p>
            <button onClick={handleGenerateQuiz} disabled={loading}>
              {loading ? 'Generating Quiz...' : 'Generate Quiz'}
            </button>
          </div>
        )}

        {quiz && (
          <div className="quiz-container">
            <h2>{quiz.quiz_title}</h2>
            {quiz.questions.map((q, index) => (
              <div key={index} className="question">
                <h3>{q.question}</h3>
                <ul className="options">
                  {q.options.map((option, opIndex) => (
                    <li key={opIndex} className={option.label === q.correct_answer ? 'correct' : ''}>
                      {option.label}. {option.text}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
