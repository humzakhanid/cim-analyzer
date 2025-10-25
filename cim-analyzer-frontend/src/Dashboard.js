import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@clerk/clerk-react";

// Helper to get a clean, short title for each CIM
function getCimTitle(summaryJson, fallback) {
  let summary;
  try {
    summary = typeof summaryJson === "string" ? JSON.parse(summaryJson) : summaryJson;
  } catch {
    return fallback;
  }
  const name = summary?.["COMPANY INFO"]?.Name || "Unknown Company";
  const desc = summary?.["COMPANY INFO"]?.Description || "";
  const subtitle = desc.split(" ").slice(0, 6).join(" ") + (desc.split(" ").length > 6 ? "..." : "");
  return `${name} – ${subtitle}`;
}

function Dashboard() {
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [response, setResponse] = useState(null);
  const [results, setResults] = useState([]);
  const [ratings, setRatings] = useState({});
  const [confidences, setConfidences] = useState({});
  const navigate = useNavigate();
  const { getToken, isSignedIn, signOut } = useAuth();

  useEffect(() => {
    if (!isSignedIn) {
      navigate("/");
    } else {
      fetchResults();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isSignedIn]);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResponse(null);
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const jwt = await getToken();
      if (!jwt) throw new Error("No Clerk JWT found");
      const res = await fetch("http://127.0.0.1:8000/api/upload", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${jwt}`,
        },
        body: formData,
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);

      const result = await res.json();
      setResponse(result);
      fetchResults();
    } catch (error) {
      setResponse({ error: "Upload failed. Please try again." });
    } finally {
      setLoading(false);
    }
  };

  const fetchResults = async () => {
    try {
      const jwt = await getToken();
      if (!jwt) throw new Error("No Clerk JWT found");
      const res = await fetch("http://127.0.0.1:8000/api/results", {
        headers: {
          Authorization: `Bearer ${jwt}`,
        },
      });

      if (res.status === 401) {
        navigate("/");
        return;
      }

      const data = await res.json();
      // Sort by recency (most recent first)
      data.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
      setResults(data);
      
      // Load existing ratings and confidence values
      const ratingsData = {};
      const confidencesData = {};
      
      data.forEach(result => {
        if (result.user_rating) {
          // Convert 1-5 rating back to thumbs up/down
          ratingsData[result.id] = result.user_rating >= 3 ? "up" : "down";
        }
        if (result.confidence_score !== null) {
          // Convert 0-1 confidence back to percentage
          confidencesData[result.id] = Math.round(result.confidence_score * 100);
        }
      });
      
      setRatings(ratingsData);
      setConfidences(confidencesData);
    } catch (error) {
      console.error("Error fetching results:", error);
    }
  };

  const handleLogout = async () => {
    try {
      await signOut();
      navigate("/");
    } catch (error) {
      console.error("Error signing out:", error);
      // Fallback: just navigate to home
      navigate("/");
    }
  };

  // Rating and confidence handlers (now persistent)
  const handleThumb = async (id, value) => {
    try {
      const jwt = await getToken();
      if (!jwt) throw new Error("No Clerk JWT found");
      
      // Convert thumbs up/down to 1-5 rating
      const rating = value === "up" ? 5 : 1;
      
      const res = await fetch(`http://127.0.0.1:8000/api/results/${id}/rating`, {
        method: "PUT",
        headers: {
          "Authorization": `Bearer ${jwt}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ rating }),
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);

      // Update local state
      setRatings((prev) => ({ ...prev, [id]: value }));
      
      // Update results to reflect the new rating
      setResults(prev => prev.map(result => 
        result.id === id ? { ...result, user_rating: rating } : result
      ));
    } catch (error) {
      console.error("Error updating rating:", error);
      alert("Failed to update rating. Please try again.");
    }
  };

  const handleConfidence = async (id, value) => {
    if (value < 0) value = 0;
    if (value > 100) value = 100;
    
    try {
      const jwt = await getToken();
      if (!jwt) throw new Error("No Clerk JWT found");
      
      // Convert percentage to 0-1 scale
      const confidence = value / 100;
      
      const res = await fetch(`http://127.0.0.1:8000/api/results/${id}/confidence`, {
        method: "PUT",
        headers: {
          "Authorization": `Bearer ${jwt}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ confidence }),
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);

      // Update local state
      setConfidences((prev) => ({ ...prev, [id]: value }));
      
      // Update results to reflect the new confidence
      setResults(prev => prev.map(result => 
        result.id === id ? { ...result, confidence_score: confidence } : result
      ));
    } catch (error) {
      console.error("Error updating confidence:", error);
      alert("Failed to update confidence. Please try again.");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this CIM analysis?")) {
      return;
    }

    try {
      const jwt = await getToken();
      if (!jwt) throw new Error("No Clerk JWT found");
      
      const res = await fetch(`http://127.0.0.1:8000/api/results/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${jwt}` },
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);

      // Remove from local state
      setResults(prev => prev.filter(result => result.id !== id));
    } catch (error) {
      console.error("Error deleting CIM:", error);
      alert("Failed to delete CIM. Please try again.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-4xl mx-auto bg-white shadow-md rounded-xl p-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">CIMLens Dashboard</h1>
          <button
            onClick={handleLogout}
            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
          >
            Logout
          </button>
        </div>

        {/* Upload Section */}
        <div className="mb-8 p-6 bg-gray-50 rounded-lg">
          <h2 className="text-xl font-semibold mb-4">Upload New CIM</h2>
          <div className="flex flex-col space-y-4">
            <input
              type="file"
              onChange={handleFileChange}
              className="border rounded px-3 py-2 w-full"
            />
            <button
              onClick={handleUpload}
              disabled={loading || !file}
              className="bg-blue-600 text-white px-6 py-2 rounded disabled:opacity-50 hover:bg-blue-700 transition"
            >
              {loading ? "Analyzing..." : "Upload and Analyze"}
            </button>
          </div>

          {response && (
            <div className="mt-4 space-y-2">
              {response.error ? (
                <p className="text-red-600 font-medium">{response.error}</p>
              ) : (
                <div>
                  <h3 className="font-semibold">Filename:</h3>
                  <p>{response.filename}</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Results Section */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Your CIM Analysis Bank</h2>
          {results.length > 0 ? (
            <div className="flex flex-col space-y-4 max-h-[60vh] overflow-y-auto">
              {results.map((res) => (
                <div
                  key={res.id}
                  className="flex flex-row items-center justify-between bg-white border rounded-lg shadow p-6"
                >
                  <div className="flex-1 min-w-0 text-left">
                    <h3
                      className="font-bold text-lg mb-1 truncate"
                      title={getCimTitle(res.summary_json, res.filename)}
                    >
                      {getCimTitle(res.summary_json, res.filename)}
                    </h3>
                    <p className="text-xs text-gray-500 mb-2 truncate">
                      {new Date(res.timestamp).toLocaleString()}
                    </p>
                    <button
                      className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition mt-2"
                      onClick={() => navigate(`/analysis/${res.id}`)}
                    >
                      View Analysis
                    </button>
                  </div>
                  <div className="flex flex-col items-center ml-6">
                    <div className="flex items-center space-x-2 mb-2">
                      <button
                        className={`rounded-full border p-2 transition-colors ${
                          ratings[res.id] === "up"
                            ? "bg-green-100 border-green-500 text-green-700"
                            : "bg-gray-100 border-gray-300 text-gray-400 hover:text-green-500"
                        }`}
                        onClick={() => handleThumb(res.id, "up")}
                        title="Thumbs Up"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                        </svg>
                      </button>
                      <button
                        className={`rounded-full border p-2 transition-colors ${
                          ratings[res.id] === "down"
                            ? "bg-red-100 border-red-500 text-red-700"
                            : "bg-gray-100 border-gray-300 text-gray-400 hover:text-red-500"
                        }`}
                        onClick={() => handleThumb(res.id, "down")}
                        title="Thumbs Down"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                      <button
                        className="rounded-full border p-2 transition-colors bg-gray-100 border-gray-300 text-gray-400 hover:text-red-500 hover:bg-red-50"
                        onClick={() => handleDelete(res.id)}
                        title="Delete CIM"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                    <div className="flex items-center space-x-2">
                      <input
                        type="range"
                        min={0}
                        max={100}
                        value={confidences[res.id] ?? (res.confidence_score ? Math.round(res.confidence_score * 100) : 50)}
                        onChange={(e) => handleConfidence(res.id, Number(e.target.value))}
                        className="w-24 accent-blue-600"
                        title="Confidence (0-100%)"
                      />
                      <span className="ml-1 text-sm font-semibold text-blue-700 w-8 text-right">
                        {confidences[res.id] ?? (res.confidence_score ? Math.round(res.confidence_score * 100) : 50)}%
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-gray-500 text-center py-8">No CIMs uploaded yet. Upload your first CIM to get started!</div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
