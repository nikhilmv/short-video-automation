"use client";

import { useState, useEffect } from "react";
import axios from "axios";

export default function CreationsPage() {
  const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:5000";
  const [creations, setCreations] = useState([]);
  const [storyText, setStoryText] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [selectedVideo, setSelectedVideo] = useState(null);

  const fetchCreations = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/creations`, {
        withCredentials: true,
      }); 
      if (response.data.success) {
        setCreations(response.data.creations || []);
      }
    } catch (err) {
      console.error("Failed to fetch creations", err);
    }
  };

  useEffect(() => {
    fetchCreations();
  }, []);

  // Poll for updates if any creation is pending or processing
  useEffect(() => {
    const hasActiveJob = creations.some(
      (c) => c.status === "pending" || c.status === "processing"
    );

    if (!hasActiveJob) return;

    const interval = setInterval(() => {
      fetchCreations();
    }, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, [creations]);

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!storyText.trim()) {
      setError("Please enter a story to generate a video.");
      return;
    }

    setError("");
    setSubmitting(true);

    try {
      const response = await axios.post(
        `${BACKEND_URL}/api/creations/generate`,
        { story_text: storyText.trim() },
        { withCredentials: true }
      );

      if (response.data.success) {
        setStoryText("");
        fetchCreations();
      } else {
        setError(response.data.message || "Failed to start video generation");
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.response?.data?.message || "Failed to generate video");
    } finally {
      setSubmitting(false);
    }
  };

  const renderStatusBadge = (status) => {
    switch (status) {
      case "completed":
        return <span className="badge bg-green-100 text-green-700">Completed</span>;
      case "processing":
        return <span className="badge bg-blue-100 text-blue-700 animate-pulse">Processing...</span>;
      case "pending":
        return <span className="badge bg-yellow-100 text-yellow-700">Pending</span>;
      case "failed":
        return <span className="badge bg-red-100 text-red-700">Failed</span>;
      default:
        return <span className="badge bg-gray-100 text-gray-600">{status}</span>;
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Creations</h1>
      </div>

      {/* Story to Video Input Card */}
      <div className="card mb-6">
        <h2 className="text-base font-semibold mb-2">Create New Video</h2>
        <p className="text-sm text-gray-500 mb-4">
          Enter your story narrative below. AI will automatically segment scenes, find matching visual clips, and generate synchronized subtitles with voiceover.
        </p>

        <form onSubmit={handleGenerate}>
          <div className="field">
            <label htmlFor="storyText" className="label">
              Story Text
            </label>
            <textarea
              id="storyText"
              rows={4}
              className="input resize-y"
              placeholder="Write or paste your story here (e.g., Every night, Rahul promised himself tomorrow would be different...)"
              value={storyText}
              onChange={(e) => setStoryText(e.target.value)}
              disabled={submitting}
            />
          </div>

          {error && <p className="error-text mb-4">{error}</p>}

          <div className="flex justify-end">
            <button
              type="submit"
              className="btn-primary"
              disabled={submitting || !storyText.trim()}
            >
              {submitting ? "Starting Generation..." : "Generate Video"}
            </button>
          </div>
        </form>
      </div>

      {/* Video Modal Preview if open */}
      {selectedVideo && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
          onClick={() => setSelectedVideo(null)}
        >
          {/* Modal */}
          <div
            className="relative w-full max-w-3xl rounded-xl bg-white p-5 shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close button */}
            <button
              type="button"
              onClick={() => setSelectedVideo(null)}
              className="absolute right-3 top-3 text-2xl text-gray-600 hover:text-black"
              aria-label="Close video"
            >
              &times;
            </button>

            {/* Modal title */}
            <h2 className="mb-4 pr-8 text-lg font-semibold text-gray-900">
              Watch Video
            </h2>

            {/* Video player */}
            <video
              key={selectedVideo.video_url}
              src={`${BACKEND_URL}${selectedVideo.video_url}`}
              controls
              autoPlay
              playsInline
              className="max-h-[75vh] w-full rounded-lg bg-black"
            >
              Your browser does not support the video tag.
            </video>
          </div>
        </div>
      )}

      {/* Creations Table */}
      <div className="table-wrap">
        <table className="table">
          <thead>
            <tr>
              <th style={{ width: "80px" }}>ID</th>
              <th>Story</th>
              <th style={{ width: "140px" }}>Status</th>
              <th style={{ width: "160px" }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {creations.map((creation) => (
              <tr key={creation.id}>
                <td className="font-medium text-gray-500">#{creation.id}</td>
                <td className="max-w-md">
                  <p className="line-clamp-2 text-ink">{creation.story_text}</p>
                </td>
                <td>{renderStatusBadge(creation.status)}</td>
                <td>
                  {creation.status === "completed" && creation.video_url ? (
                    <div className="flex items-center gap-3">
                      <button
                        type="button"
                        onClick={() => setSelectedVideo(creation)}
                        className="text-brand-600 hover:underline font-medium text-sm"
                      >
                        Watch Video
                      </button>
                      <a
                        href={`${BACKEND_URL}${creation.video_url}`}
                        target="_blank"
                        rel="noreferrer"
                        download
                        className="text-xs text-gray-500 hover:underline"
                      >
                        Download
                      </a>
                    </div>
                  ) : creation.status === "processing" || creation.status === "pending" ? (
                    <span className="text-xs text-gray-400">Rendering video...</span>
                  ) : (
                    <span className="text-xs text-red-500">Generation failed</span>
                  )}
                </td>
              </tr>
            ))}
            {creations.length === 0 && (
              <tr>
                <td colSpan={4} className="text-center text-gray-500 py-8">
                  No creations yet. Enter a story above to generate your first video!
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
