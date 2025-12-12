import { useState, useEffect } from 'react'
import axios from 'axios'
import { FaRobot, FaSearch, FaCheckCircle, FaExclamationCircle, FaTrash } from 'react-icons/fa'
import './App.css'

const API_BASE_URL = "http://localhost:6543/api";

function App() {
  const [reviews, setReviews] = useState([]);
  const [formData, setFormData] = useState({
    product_name: '',
    review_text: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchReviews();
  }, []);

  const fetchReviews = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/reviews`);
      setReviews(response.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await axios.post(`${API_BASE_URL}/analyze-review`, formData);
      setFormData({ product_name: '', review_text: '' });
      fetchReviews();
    } catch (err) {
      setError(err.response?.data?.error || "Gagal menganalisis review.");
    } finally {
      setLoading(false);
    }
  };

  
  const handleClear = async () => {
    if (!confirm("Yakin ingin menghapus semua riwayat analisis?")) return;
    
    try {
      await axios.post(`${API_BASE_URL}/clear-reviews`);
      setReviews([]);
    } catch (err) {
      alert("Gagal menghapus data.");
    }
  };

  const getSentimentStyle = (sentiment) => {
    if (sentiment === 'POSITIVE') return { color: '#155724', bg: '#d4edda', border: '#c3e6cb', icon: <FaCheckCircle /> };
    if (sentiment === 'NEGATIVE') return { color: '#721c24', bg: '#f8d7da', border: '#f5c6cb', icon: <FaExclamationCircle /> };
    return { color: '#856404', bg: '#fff3cd', border: '#ffeeba', icon: <FaSearch /> };
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-content">
          <h1> Product Review Analyzer</h1>
        </div>
      </header>

      <main className="main-content">
        <section className="input-section">
          <div className="form-card">
            <h2> Analyze New Review</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Product Name</label>
                <input
                  type="text"
                  value={formData.product_name}
                  onChange={(e) => setFormData({...formData, product_name: e.target.value})}
                  placeholder="e.g. iPhone 15 Pro, Starbucks Coffee..."
                  required
                />
              </div>
              
              <div className="form-group">
                <label>Review Text (English)</label>
                <textarea
                  rows="4"
                  value={formData.review_text}
                  onChange={(e) => setFormData({...formData, review_text: e.target.value})}
                  placeholder="e.g. I absolutely love this product! The quality is amazing."
                  required
                />
              </div>

              {error && <div className="error-message">{error}</div>}

              <button type="submit" className="analyze-btn" disabled={loading}>
                {loading ? (
                  <span className="loading-text">⚙️ Analyzing...</span>
                ) : (
                  <>Analyze Sentiment & Extract Points</>
                )}
              </button>
            </form>
          </div>
        </section>

        <section className="results-section">
          {/* HEADER DENGAN TOMBOL DELETE */}
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px'}}>
            <h2>📊 Analysis History</h2>
            {reviews.length > 0 && (
              <button 
                onClick={handleClear}
                style={{
                  padding: '8px 12px',
                  backgroundColor: '#dc3545',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontWeight: 'bold',
                  fontSize: '0.9rem'
                }}
              >
                <FaTrash /> Clear History
              </button>
            )}
          </div>
          
          {reviews.length === 0 && (
            <div className="empty-state">
              <p>Belum ada data review. Coba input review baru di atas!</p>
            </div>
          )}

          <div className="review-grid">
            {reviews.map((review) => {
              const style = getSentimentStyle(review.sentiment);
              return (
                <div key={review.id} className="review-card">
                  <div className="card-header">
                    <h3>{review.product_name}</h3>
                    <span className="date">{new Date(review.created_at).toLocaleDateString()}</span>
                  </div>
                  
                  <p className="review-text">"{review.review_text}"</p>

                  <div className="analysis-box">
                    <div className="sentiment-badge" style={{ backgroundColor: style.bg, color: style.color, borderColor: style.border }}>
                      {style.icon} <strong>{review.sentiment}</strong> 
                      <span className="confidence">Confidence: {(review.confidence * 100).toFixed(1)}%</span>
                    </div>

                    <div className="key-points">
                      <h4>💡 Key Points (Gemini):</h4>
                      <ul>
                        {review.key_points && review.key_points.map((point, idx) => (
                          <li key={idx}>{point}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      </main>
    </div>
  )
}

export default App