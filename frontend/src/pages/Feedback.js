import React, { useState, useEffect } from "react";
import { toast } from "react-hot-toast";
import {
  MessageCircle,
  Send,
  ThumbsUp,
  ThumbsDown,
  Star,
  Filter,
  Search,
} from "lucide-react";
import LoadingSpinner from "../components/LoadingSpinner";
import { useAuth } from "../utils/AuthContext";
import { api } from "../utils/api";

const Feedback = () => {
  const { token } = useAuth();
  const [feedback, setFeedback] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterRating, setFilterRating] = useState("all");
  const [filterSentiment, setFilterSentiment] = useState("all");
  const [sentimentAnalysis, setSentimentAnalysis] = useState({});
  const [showReplyModal, setShowReplyModal] = useState(false);
  const [replyingTo, setReplyingTo] = useState(null);
  const [replyText, setReplyText] = useState("");

  useEffect(() => {
    fetchFeedback();
    fetchSentimentAnalysis();
  }, []);

  const fetchFeedback = async () => {
    try {
      setLoading(true);
      const response = await api.get("/api/v1/feedback");
      setFeedback(response.data?.feedback || response.feedback || []);
    } catch (error) {
      console.error("Error fetching feedback:", error);
      // Fallback to empty data
      setFeedback([]);
      toast.error("Failed to load feedback");
    } finally {
      setLoading(false);
    }
  };

  const fetchSentimentAnalysis = async () => {
    try {
      const response = await api.get("/api/v1/feedback/sentiment");
      setSentimentAnalysis(response.data?.analysis || response.analysis || {});
    } catch (error) {
      console.error("Error fetching sentiment analysis:", error);
      setSentimentAnalysis({
        overall_sentiment: "neutral",
        sentiment_distribution: { positive: 0, neutral: 0, negative: 0 },
        trending_topics: [],
      });
      toast.error("Failed to load sentiment analysis");
    }
  };

  const replyToFeedback = async () => {
    try {
      await api.post(
        `/feedback/${replyingTo.id}/reply`,
        {
          response: replyText,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        },
      );
      fetchFeedback();
      setShowReplyModal(false);
      setReplyingTo(null);
      setReplyText("");
    } catch (error) {
      console.error("Error replying to feedback:", error);
    }
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case "positive":
        return "text-green-600 bg-green-100";
      case "negative":
        return "text-red-600 bg-red-100";
      case "neutral":
        return "text-yellow-600 bg-yellow-100";
      default:
        return "text-gray-600 bg-gray-100";
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "responded":
        return "text-blue-600 bg-blue-100";
      case "pending":
        return "text-orange-600 bg-orange-100";
      default:
        return "text-gray-600 bg-gray-100";
    }
  };

  const renderStars = (rating) => {
    return [...Array(5)].map((_, i) => (
      <Star
        key={i}
        className={`h-4 w-4 ${
          i < rating ? "text-yellow-400 fill-current" : "text-gray-300"
        }`}
      />
    ));
  };

  const filteredFeedback = feedback.filter((item) => {
    const matchesSearch =
      item.customer_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.product_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.comment.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesRating =
      filterRating === "all" || item.rating === parseInt(filterRating);
    const matchesSentiment =
      filterSentiment === "all" || item.sentiment === filterSentiment;

    return matchesSearch && matchesRating && matchesSentiment;
  });

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Customer Feedback
          </h1>
          <p className="text-gray-600">
            Monitor and respond to customer feedback with AI-powered sentiment
            analysis
          </p>
        </div>

        {/* Sentiment Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Overall Sentiment
                </p>
                <p className="text-2xl font-bold capitalize text-gray-900">
                  {sentimentAnalysis.overall_sentiment}
                </p>
              </div>
              <MessageCircle className="h-8 w-8 text-blue-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Positive</p>
                <p className="text-2xl font-bold text-green-600">
                  {sentimentAnalysis.sentiment_distribution?.positive || 0}%
                </p>
              </div>
              <ThumbsUp className="h-8 w-8 text-green-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Neutral</p>
                <p className="text-2xl font-bold text-yellow-600">
                  {sentimentAnalysis.sentiment_distribution?.neutral || 0}%
                </p>
              </div>
              <MessageCircle className="h-8 w-8 text-yellow-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Negative</p>
                <p className="text-2xl font-bold text-red-600">
                  {sentimentAnalysis.sentiment_distribution?.negative || 0}%
                </p>
              </div>
              <ThumbsDown className="h-8 w-8 text-red-500" />
            </div>
          </div>
        </div>

        {/* Trending Topics */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Trending Topics
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {sentimentAnalysis.trending_topics?.map((topic, index) => (
              <div
                key={index}
                className="p-4 border border-gray-200 rounded-lg"
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900 capitalize">
                    {topic.topic}
                  </h4>
                  <span
                    className={`px-2 py-1 text-xs font-semibold rounded-full ${getSentimentColor(topic.sentiment)}`}
                  >
                    {topic.sentiment}
                  </span>
                </div>
                <p className="text-sm text-gray-600">
                  {topic.mentions} mentions
                </p>
              </div>
            )) || []}
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search feedback..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <select
              value={filterRating}
              onChange={(e) => setFilterRating(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Ratings</option>
              <option value="5">5 Stars</option>
              <option value="4">4 Stars</option>
              <option value="3">3 Stars</option>
              <option value="2">2 Stars</option>
              <option value="1">1 Star</option>
            </select>

            <select
              value={filterSentiment}
              onChange={(e) => setFilterSentiment(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Sentiments</option>
              <option value="positive">Positive</option>
              <option value="neutral">Neutral</option>
              <option value="negative">Negative</option>
            </select>
          </div>
        </div>

        {/* Feedback List */}
        <div className="space-y-6">
          {filteredFeedback.map((item) => (
            <div key={item.id} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="font-semibold text-lg text-gray-900">
                    {item.customer_name}
                  </h3>
                  <p className="text-sm text-gray-600">{item.customer_email}</p>
                  <p className="text-sm text-gray-600">{item.product_name}</p>
                </div>
                <div className="text-right">
                  <div className="flex items-center mb-2">
                    {renderStars(item.rating)}
                    <span className="ml-2 text-sm text-gray-600">
                      ({item.rating}/5)
                    </span>
                  </div>
                  <div className="flex space-x-2">
                    <span
                      className={`px-2 py-1 text-xs font-semibold rounded-full ${getSentimentColor(item.sentiment)}`}
                    >
                      {item.sentiment}
                    </span>
                    <span
                      className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(item.status)}`}
                    >
                      {item.status}
                    </span>
                  </div>
                </div>
              </div>

              <div className="mb-4">
                <p className="text-gray-700">{item.comment}</p>
                <p className="text-sm text-gray-500 mt-2">{item.date}</p>
              </div>

              {item.response && (
                <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-4">
                  <p className="text-sm font-medium text-blue-800">
                    Your Response:
                  </p>
                  <p className="text-blue-700">{item.response}</p>
                </div>
              )}

              {!item.response && (
                <button
                  onClick={() => {
                    setReplyingTo(item);
                    setShowReplyModal(true);
                  }}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
                >
                  <Send className="h-4 w-4 mr-2" />
                  Reply
                </button>
              )}
            </div>
          ))}
        </div>

        {filteredFeedback.length === 0 && (
          <div className="text-center py-12">
            <MessageCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No feedback found
            </h3>
            <p className="text-gray-600">
              Try adjusting your filters or search terms
            </p>
          </div>
        )}

        {/* Reply Modal */}
        {showReplyModal && replyingTo && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
              <h3 className="text-lg font-bold text-gray-900 mb-4">
                Reply to {replyingTo.customer_name}
              </h3>

              <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600 font-medium">
                  Original Feedback:
                </p>
                <p className="text-sm text-gray-700">{replyingTo.comment}</p>
              </div>

              <textarea
                value={replyText}
                onChange={(e) => setReplyText(e.target.value)}
                placeholder="Type your response..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={4}
              />

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => {
                    setShowReplyModal(false);
                    setReplyingTo(null);
                    setReplyText("");
                  }}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
                >
                  Cancel
                </button>
                <button
                  onClick={replyToFeedback}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
                >
                  <Send className="h-4 w-4 mr-2" />
                  Send Reply
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Feedback;
