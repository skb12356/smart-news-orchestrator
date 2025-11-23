import React, { useState, useEffect } from 'react';
import { TrendingUp, AlertTriangle, BarChart3, Calendar, ExternalLink, X, PieChart, Activity, Sparkles, Star } from 'lucide-react';

const Dashboard = () => {
  const [articles, setArticles] = useState([]);
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedRisk, setSelectedRisk] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const response = await fetch('/agents/risk_agent/risk_assessment_results.json');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('✅ Loaded data:', data);
        
        if (data.detailed_results && Array.isArray(data.detailed_results)) {
          const articlesData = data.detailed_results.map((article, idx) => ({
            id: idx,
            title: article.title || 'Untitled',
            content: article.content_text || article.content || 'No content available',
            url: article.url || '#',
            published_date: article.published_time || article.published_date || 'Unknown date',
            risk_score: (article.risk_analysis?.risk_score || 0) * 100,
            risk_level: article.risk_analysis?.risk_score >= 0.7 ? 'HIGH' : 
                       article.risk_analysis?.risk_score >= 0.4 ? 'MEDIUM' : 'LOW',
            sentiment_label: article.risk_analysis?.sentiment_label || article.sentiment || 'neutral',
            sentiment_score: article.risk_analysis?.sentiment_score || 0,
            risk_categories: article.risk_analysis?.risk_category?.reduce((acc, cat) => {
              acc[cat] = article.risk_analysis?.risk_score || 0;
              return acc;
            }, {}) || {},
            article_number: idx + 1  // Use sequential numbering (1-22)
          }));
          
          console.log('📊 Extracted articles:', articlesData.length);
          setArticles(articlesData);
        } else {
          console.warn('⚠️ No detailed_results found in data');
          setArticles([]);
        }
        setLoading(false);
      } catch (error) {
        console.error('❌ Error loading data:', error);
        setArticles([]);
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const calculateStats = () => {
    if (articles.length === 0) return { high: 0, medium: 0, low: 0, total: 0, avgRisk: 0 };
    
    const high = articles.filter(a => a.risk_level === 'HIGH').length;
    const medium = articles.filter(a => a.risk_level === 'MEDIUM').length;
    const low = articles.filter(a => a.risk_level === 'LOW').length;
    const avgRisk = articles.reduce((sum, a) => sum + a.risk_score, 0) / articles.length;
    
    return { high, medium, low, total: articles.length, avgRisk };
  };

  const groupByCategory = () => {
    const categories = {};
    articles.forEach(article => {
      Object.keys(article.risk_categories || {}).forEach(cat => {
        if (!categories[cat]) categories[cat] = 0;
        categories[cat]++;
      });
    });
    return Object.entries(categories).sort((a, b) => b[1] - a[1]);
  };

  const getFilteredArticles = () => {
    return articles.filter(article => {
      const categoryMatch = selectedCategory === 'all' || 
        Object.keys(article.risk_categories || {}).includes(selectedCategory);
      const riskMatch = selectedRisk === 'all' || article.risk_level === selectedRisk;
      return categoryMatch && riskMatch;
    });
  };

  const stats = calculateStats();
  const categories = groupByCategory();
  const filteredArticles = getFilteredArticles();

  const getRiskColor = (level) => {
    switch(level) {
      case 'HIGH': return 'from-red-500 to-rose-600';
      case 'MEDIUM': return 'from-yellow-500 to-amber-600';
      case 'LOW': return 'from-green-500 to-emerald-600';
      default: return 'from-gray-500 to-slate-600';
    }
  };

  const getSentimentColor = (label) => {
    switch(label?.toLowerCase()) {
      case 'positive': return 'text-green-400';
      case 'negative': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-purple-500 mx-auto"></div>
          <p className="text-white mt-4 text-lg">Loading Risk Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">Financial News Risk Dashboard</h1>
        <p className="text-gray-600">Real-time market sentiment and risk analysis</p>
      </div>

      {/* Stats Cards */}
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-red-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">High Risk</p>
              <p className="text-3xl font-bold text-gray-800">{stats.high}</p>
            </div>
            <AlertTriangle className="w-8 h-8 text-red-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-yellow-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Medium Risk</p>
              <p className="text-3xl font-bold text-gray-800">{stats.medium}</p>
            </div>
            <BarChart3 className="w-8 h-8 text-yellow-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Low Risk</p>
              <p className="text-3xl font-bold text-gray-800">{stats.low}</p>
            </div>
            <TrendingUp className="w-8 h-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Avg Risk Score</p>
              <p className="text-3xl font-bold text-gray-800">{stats.avgRisk.toFixed(1)}%</p>
            </div>
            <PieChart className="w-8 h-8 text-blue-500" />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="max-w-7xl mx-auto mb-6 flex gap-4 flex-wrap">
        <select 
          value={selectedRisk}
          onChange={(e) => setSelectedRisk(e.target.value)}
          className="bg-white border border-gray-300 rounded-lg px-4 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="all">All Risk Levels</option>
          <option value="HIGH">High Risk</option>
          <option value="MEDIUM">Medium Risk</option>
          <option value="LOW">Low Risk</option>
        </select>

        <select 
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="bg-white border border-gray-300 rounded-lg px-4 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="all">All Categories</option>
          {categories.map(([cat, count]) => (
            <option key={cat} value={cat}>{cat} ({count})</option>
          ))}
        </select>

        <div className="ml-auto text-gray-700 bg-white rounded-lg px-4 py-2 border border-gray-300">
          Showing {filteredArticles.length} of {stats.total} articles
        </div>
      </div>

      {/* Articles Grid */}
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredArticles.map((article) => (
          <div
            key={article.id}
            onClick={() => setSelectedArticle(article)}
            className="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 cursor-pointer overflow-hidden"
          >
            <div className="p-6">
              <div className="flex items-start justify-between mb-3">
                <div className={`px-3 py-1 rounded text-xs font-bold text-white bg-gradient-to-r ${getRiskColor(article.risk_level)}`}>
                  {article.risk_level}
                </div>
                <div className="text-gray-500 text-sm flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  {new Date(article.published_date).toLocaleDateString()}
                </div>
              </div>

              <h3 className="text-gray-800 font-bold text-lg mb-3 line-clamp-2">
                {article.title}
              </h3>

              <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                {article.content.substring(0, 200)}...
              </p>

              <div className="flex flex-wrap gap-2 mb-4">
                {Object.keys(article.risk_categories || {}).slice(0, 3).map((cat) => (
                  <span key={cat} className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-xs">
                    {cat}
                  </span>
                ))}
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                <div className="flex items-center gap-2">
                  <div className={`font-semibold text-sm ${getSentimentColor(article.sentiment_label)}`}>
                    {article.sentiment_label?.toUpperCase()}
                  </div>
                  <div className="text-gray-500 text-sm">
                    {(article.sentiment_score * 100).toFixed(0)}%
                  </div>
                </div>
                <div className="text-gray-800 font-bold text-lg">
                  {article.risk_score.toFixed(0)}%
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Article Detail Modal */}
      {selectedArticle && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-md flex items-center justify-center p-4 z-50 animate-in fade-in duration-300">
          <div className="bg-white rounded-3xl max-w-6xl w-full max-h-[90vh] overflow-hidden shadow-2xl relative">
            
            <div className="overflow-y-auto max-h-[90vh]">
              {/* Modern Header */}
              <div className="bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 p-8">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="bg-white/20 backdrop-blur-sm rounded-full p-2">
                        <Sparkles className="w-6 h-6 text-yellow-300" />
                      </div>
                      <h2 className="text-3xl font-bold text-white leading-tight pr-8">
                        {selectedArticle.title}
                      </h2>
                    </div>
                    <div className="flex items-center gap-4 text-white/90 text-sm">
                      <span className="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-3 py-1.5 rounded-full">
                        <Calendar className="w-4 h-4" />
                        {new Date(selectedArticle.published_date).toLocaleDateString('en-US', { 
                          year: 'numeric', month: 'long', day: 'numeric' 
                        })}
                      </span>
                      <span className="bg-white/10 backdrop-blur-sm px-3 py-1.5 rounded-full">Article #{selectedArticle.article_number}</span>
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedArticle(null)}
                    className="bg-white/20 hover:bg-white/30 backdrop-blur-sm text-white rounded-full p-2.5 transition-all duration-200 hover:scale-110 hover:rotate-90"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>

                <div className="flex gap-3 flex-wrap">
                  <div className={`px-5 py-2.5 rounded-xl text-sm font-bold text-white bg-gradient-to-r ${getRiskColor(selectedArticle.risk_level)} shadow-lg flex items-center gap-2`}>
                    <AlertTriangle className="w-4 h-4" />
                    {selectedArticle.risk_level} RISK
                  </div>
                  <div className="px-5 py-2.5 rounded-xl text-sm font-semibold bg-white/20 text-white backdrop-blur-sm">
                    Risk Score: {selectedArticle.risk_score.toFixed(1)}%
                  </div>
                  <div className={`px-5 py-2.5 rounded-xl text-sm font-semibold bg-white/20 backdrop-blur-sm text-white`}>
                    {selectedArticle.sentiment_label?.toUpperCase()} ({(selectedArticle.sentiment_score * 100).toFixed(0)}%)
                  </div>
                </div>
              </div>

              {/* Stats Cards */}
              <div className="grid grid-cols-3 gap-6 p-8 bg-gray-50">
                <div className="bg-white rounded-2xl p-6 shadow-lg border-2 border-red-100 hover:shadow-xl transition-all duration-300 hover:scale-105">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="bg-gradient-to-br from-red-500 to-rose-600 p-3 rounded-xl shadow-md">
                      <AlertTriangle className="w-6 h-6 text-white" />
                    </div>
                    <h4 className="text-gray-700 font-bold">Risk Assessment</h4>
                  </div>
                  <p className="text-4xl font-bold bg-gradient-to-r from-red-600 to-rose-600 bg-clip-text text-transparent mb-2">
                    {selectedArticle.risk_score.toFixed(1)}%
                  </p>
                  <p className="text-gray-500 text-sm font-medium">{selectedArticle.risk_level} priority level</p>
                </div>

                <div className="bg-white rounded-2xl p-6 shadow-lg border-2 border-blue-100 hover:shadow-xl transition-all duration-300 hover:scale-105">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="bg-gradient-to-br from-blue-500 to-cyan-600 p-3 rounded-xl shadow-md">
                      <Activity className="w-6 h-6 text-white" />
                    </div>
                    <h4 className="text-gray-700 font-bold">Sentiment Score</h4>
                  </div>
                  <p className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent mb-2">
                    {(selectedArticle.sentiment_score * 100).toFixed(0)}%
                  </p>
                  <p className="text-gray-500 text-sm font-medium capitalize">{selectedArticle.sentiment_label} outlook</p>
                </div>

                <div className="bg-white rounded-2xl p-6 shadow-lg border-2 border-purple-100 hover:shadow-xl transition-all duration-300 hover:scale-105">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="bg-gradient-to-br from-purple-500 to-violet-600 p-3 rounded-xl shadow-md">
                      <PieChart className="w-6 h-6 text-white" />
                    </div>
                    <h4 className="text-gray-700 font-bold">Risk Categories</h4>
                  </div>
                  <p className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-violet-600 bg-clip-text text-transparent mb-2">
                    {Object.keys(selectedArticle.risk_categories || {}).length}
                  </p>
                  <p className="text-gray-500 text-sm font-medium">Identified factors</p>
                </div>
              </div>

              {/* Article Content */}
              <div className="px-8 py-6">
                <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-200">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="bg-gradient-to-br from-amber-400 to-yellow-500 p-2.5 rounded-lg">
                      <Star className="w-5 h-5 text-white" />
                    </div>
                    <h3 className="text-2xl font-bold text-gray-800">Article Content</h3>
                  </div>
                  <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-6 border border-gray-200 max-h-[400px] overflow-y-auto custom-scrollbar">
                    <p className="text-gray-700 leading-relaxed text-base whitespace-pre-wrap">
                      {selectedArticle.content}
                    </p>
                  </div>
                </div>
              </div>

              {/* Risk Categories */}
              {Object.keys(selectedArticle.risk_categories || {}).length > 0 && (
                <div className="px-8 pb-6">
                  <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-200">
                    <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-3">
                      <div className="bg-gradient-to-br from-indigo-500 to-purple-600 p-2.5 rounded-lg">
                        <BarChart3 className="w-5 h-5 text-white" />
                      </div>
                      Risk Breakdown
                    </h3>
                    <div className="flex flex-wrap gap-3">
                      {Object.entries(selectedArticle.risk_categories).map(([category, score]) => (
                        <div key={category} className="bg-gradient-to-br from-indigo-50 to-purple-50 px-5 py-3 rounded-xl border-2 border-indigo-200 hover:border-indigo-400 hover:scale-105 transition-all duration-200 shadow-sm">
                          <div className="text-indigo-700 text-sm font-bold uppercase tracking-wide">{category}</div>
                          <div className="text-indigo-900 font-bold text-lg">{typeof score === 'number' ? score.toFixed(2) : score}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Charts Section */}
              <div className="px-8 pb-6">
                <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-200">
                  <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-3">
                    <div className="bg-gradient-to-br from-teal-500 to-cyan-600 p-2.5 rounded-lg">
                      <BarChart3 className="w-5 h-5 text-white" />
                    </div>
                    Visual Analytics
                  </h3>
                  <div className="grid grid-cols-2 gap-6">
                    <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-6 border-2 border-gray-200 hover:border-indigo-300 transition-all">
                      <h4 className="text-gray-700 font-bold mb-4 text-sm uppercase tracking-wide">Risk Score Gauge</h4>
                      <img 
                        src={`/agents/charts/article${selectedArticle.article_number}_1.png`}
                        alt="Risk Gauge"
                        className="w-full rounded-lg shadow-md"
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'flex';
                        }}
                      />
                      <div className="hidden items-center justify-center h-48 text-gray-400 bg-gray-100 rounded-lg">
                        <p className="font-medium">Chart not available</p>
                      </div>
                    </div>
                    <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-6 border-2 border-gray-200 hover:border-purple-300 transition-all">
                      <h4 className="text-gray-700 font-bold mb-4 text-sm uppercase tracking-wide">Sentiment & Categories</h4>
                      <img 
                        src={`/agents/charts/article${selectedArticle.article_number}_2.png`}
                        alt="Sentiment Analysis"
                        className="w-full rounded-lg shadow-md"
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'flex';
                        }}
                      />
                      <div className="hidden items-center justify-center h-48 text-gray-400 bg-gray-100 rounded-lg">
                        <p className="font-medium">Chart not available</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Source Link */}
              <div className="px-8 pb-8">
                <a
                  href={selectedArticle.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-3 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 hover:from-indigo-700 hover:via-purple-700 hover:to-pink-700 text-white px-8 py-4 rounded-2xl font-bold text-lg transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-xl w-full justify-center"
                >
                  <ExternalLink className="w-6 h-6" />
                  Read Full Article on Source
                </a>
              </div>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(100, 100, 100, 0.2);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(168, 85, 247, 0.5);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(168, 85, 247, 0.7);
        }
      `}</style>
    </div>
  );
};

export default Dashboard;
