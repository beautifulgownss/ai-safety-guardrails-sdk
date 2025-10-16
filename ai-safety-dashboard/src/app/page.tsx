"use client";
import { useState } from "react";

export default function Page() {
  const [context, setContext] = useState("");
  const [response, setResponse] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/detect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ context, response }),
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error("Error calling backend:", err);
      setResult({ error: "Failed to connect to backend." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-zinc-950 text-white px-6 py-10">
      <h1 className="text-3xl font-bold mb-8 text-center">
        🧠 AI Safety Guardrails Dashboard
      </h1>

      <div className="w-full max-w-2xl space-y-4">
        <div>
          <label className="block text-sm font-semibold mb-2">Context</label>
          <textarea
            className="w-full p-3 rounded-md bg-zinc-900 border border-zinc-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            rows={4}
            placeholder="Paste the original prompt or context here..."
            value={context}
            onChange={(e) => setContext(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm font-semibold mb-2">Response</label>
          <textarea
            className="w-full p-3 rounded-md bg-zinc-900 border border-zinc-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            rows={4}
            placeholder="Paste the model's response here..."
            value={response}
            onChange={(e) => setResponse(e.target.value)}
          />
        </div>

        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 rounded-md font-semibold transition disabled:opacity-50"
        >
          {loading ? "Analyzing..." : "Analyze"}
        </button>

        {result && (
          <div className="mt-6 p-4 rounded-md bg-zinc-900 border border-zinc-700">
            <h2 className="text-lg font-semibold mb-2">Results</h2>
            {result.error ? (
              <p className="text-red-400">{result.error}</p>
            ) : (
              <pre className="whitespace-pre-wrap text-sm text-zinc-300">
                {JSON.stringify(result, null, 2)}
              </pre>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
