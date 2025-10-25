import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAuth } from "@clerk/clerk-react";

function renderAnalysis(summaryJson) {
  if (!summaryJson) return <div className="text-red-600">No analysis available.</div>;
  let summary;
  try {
    summary = typeof summaryJson === "string" ? JSON.parse(summaryJson) : summaryJson;
  } catch {
    return <div className="text-red-600">Invalid analysis format</div>;
  }

  return (
    <div className="space-y-6">
      <section>
        <h2 className="font-bold text-xl mb-2">Executive Summary</h2>
        <p>{summary.SUMMARY || "N/A"}</p>
      </section>
      <section>
        <h2 className="font-bold text-xl mb-2">Key Financials</h2>
        <div className="ml-4">
          <div className="font-semibold">Actuals:</div>
          <ul className="ml-4 list-disc">
            <li>Revenue: {summary.FINANCIALS?.Actuals?.revenue || "N/A"}</li>
            <li>EBITDA: {summary.FINANCIALS?.Actuals?.EBITDA || "N/A"}</li>
            <li>Year: {summary.FINANCIALS?.Actuals?.year || "N/A"}</li>
            <li>Margin: {summary.FINANCIALS?.Actuals?.margin || "N/A"}</li>
            <li>FCF: {summary.FINANCIALS?.Actuals?.FCF || "N/A"}</li>
          </ul>
          <div className="font-semibold mt-2">Estimates:</div>
          <ul className="ml-4 list-disc">
            <li>Forward Revenue: {summary.FINANCIALS?.Estimates?.["forward revenue"] || "N/A"}</li>
            <li>EBITDA: {summary.FINANCIALS?.Estimates?.EBITDA || "N/A"}</li>
            <li>Capex: {summary.FINANCIALS?.Estimates?.capex || "N/A"}</li>
            <li>Capex/Revenue: {summary.FINANCIALS?.Estimates?.["capex/revenue"] || "N/A"}</li>
          </ul>
        </div>
      </section>
      <section>
        <h2 className="font-bold text-xl mb-2">Investment Thesis</h2>
        <ul className="ml-4 list-disc">
          {(summary.THESIS && summary.THESIS.length > 0)
            ? summary.THESIS.map((t, i) => <li key={i}>{t}</li>)
            : <li>No thesis points found.</li>}
        </ul>
      </section>
      <section>
        <h2 className="font-bold text-xl mb-2">Red Flags</h2>
        <ul className="ml-4 list-disc">
          {(summary["RED FLAGS"] && summary["RED FLAGS"].length > 0)
            ? summary["RED FLAGS"].map((r, i) => <li key={i}>{r}</li>)
            : <li>No red flags found.</li>}
        </ul>
      </section>
      <section>
        <h2 className="font-bold text-xl mb-2">Confidence & Flags</h2>
        <div>Confidence Score: {summary.confidence_score ? `${Math.round(summary.confidence_score * 100)}%` : "N/A"}</div>
        <div>Flagged Fields: {summary.flagged_fields?.join(", ") || "None"}</div>
        <div>Low Confidence Notes: {summary.low_confidence_flags || "None"}</div>
      </section>
      {/* Add comments, ratings, or team collaboration features here */}
    </div>
  );
}

export default function AnalysisPage() {
  const { id } = useParams();
  const [result, setResult] = useState(null);
  const navigate = useNavigate();
  const { getToken, isSignedIn } = useAuth();

  useEffect(() => {
    if (!isSignedIn) {
      navigate("/");
      return;
    }
    
    const fetchData = async () => {
      try {
        const jwt = await getToken();
        if (!jwt) throw new Error("No Clerk JWT found");
        
        const res = await fetch(`http://127.0.0.1:8000/api/results`, {
          headers: { Authorization: `Bearer ${jwt}` },
        });
        
        if (!res.ok) throw new Error(`Server error: ${res.status}`);
        
        const data = await res.json();
        const found = data.find((r) => String(r.id) === String(id));
        setResult(found);
      } catch (error) {
        console.error("Error fetching analysis:", error);
      }
    };
    
    fetchData();
  }, [id, isSignedIn, getToken, navigate]);

  if (!result) return <div className="p-8">Loading analysis...</div>;

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-3xl mx-auto bg-white shadow-md rounded-xl p-8">
        <button
          className="mb-4 text-blue-600 hover:underline"
          onClick={() => navigate("/")}
        >
          ← Back to Dashboard
        </button>
        <h1 className="text-2xl font-bold mb-2">{result.filename}</h1>
        <p className="text-sm text-gray-500 mb-6">{new Date(result.timestamp).toLocaleString()}</p>
        {renderAnalysis(result.summary_json)}
      </div>
    </div>
  );
}
