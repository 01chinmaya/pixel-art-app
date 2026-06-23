import { useState } from "react";

// Set this to your deployed backend URL after deploying the backend service on Render.
// Example: "https://pixelart-backend.onrender.com"
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export default function App() {
  const [original, setOriginal] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [useAI, setUseAI] = useState(false);
  const [blockSize, setBlockSize] = useState(16);
  const [error, setError] = useState(null);

  const handleUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setError(null);
    setResult(null);
    setOriginal(URL.createObjectURL(file));
    processImage(file);
  };

  const processImage = async (file) => {
    setLoading(true);
    const formData = new FormData();
    formData.append("image", file);
    formData.append("use_ai", useAI);
    formData.append("block_size", blockSize);

    try {
      const res = await fetch(`${API_BASE}/api/pixelate`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("Server returned an error");
      const blob = await res.blob();
      setResult(URL.createObjectURL(blob));
    } catch (err) {
      console.error(err);
      setError("Something went wrong processing that image. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 flex flex-col items-center p-6">
      <h1 className="text-2xl font-bold mb-2">Pixel / Voxel Art Converter</h1>
      <p className="text-sm text-neutral-500 mb-6">Upload a photo, get a Minecraft-style pixel art version.</p>

      <div className="flex flex-wrap items-center gap-4 mb-6">
        <label className="bg-emerald-600 hover:bg-emerald-500 px-4 py-2 rounded-lg cursor-pointer transition">
          Upload Image
          <input type="file" accept="image/*" className="hidden" onChange={handleUpload} />
        </label>

        <div className="flex items-center gap-2 text-sm">
          <span>Block size</span>
          <input
            type="range"
            min="6"
            max="32"
            value={blockSize}
            onChange={(e) => setBlockSize(Number(e.target.value))}
          />
          <span className="w-6 text-right">{blockSize}</span>
        </div>

        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={useAI} onChange={(e) => setUseAI(e.target.checked)} />
          Enhance with AI (Voxel style)
        </label>

        {result && (
          <a
            href={result}
            download="pixelart.png"
            className="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-lg transition"
          >
            Download Result
          </a>
        )}
      </div>

      {loading && <p className="text-sm text-neutral-400 mb-4">Processing...</p>}
      {error && <p className="text-sm text-red-400 mb-4">{error}</p>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-4xl">
        <div>
          <p className="text-sm mb-2 text-neutral-400">Before</p>
          {original && <img src={original} className="rounded-lg border border-neutral-800 w-full" />}
        </div>
        <div>
          <p className="text-sm mb-2 text-neutral-400">After</p>
          {result && <img src={result} className="rounded-lg border border-neutral-800 w-full" />}
        </div>
      </div>
    </div>
  );
}
