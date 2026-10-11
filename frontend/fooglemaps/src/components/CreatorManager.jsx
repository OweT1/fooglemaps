import { useEffect, useState } from "react";

export default function CreatorManager() {
  const [creators, setCreators] = useState([]);
  const [username, setUsername] = useState("");
  const [error, setError] = useState("");

  const fetchCreators = () => {
    fetch("/api/creators")
      .then((r) => r.json())
      .then(setCreators)
      .catch(() => {});
  };

  useEffect(() => {
    fetchCreators();
  }, []);

  const addCreator = async (e) => {
    e.preventDefault();
    setError("");
    const trimmed = username.trim();
    if (!trimmed) return;

    const res = await fetch("/api/creators", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: trimmed }),
    });

    if (res.ok) {
      setUsername("");
      fetchCreators();
    } else {
      const data = await res.json();
      setError(data.detail || "Failed to add creator");
    }
  };

  const removeCreator = async (id) => {
    await fetch(`/api/creators/${id}`, { method: "DELETE" });
    fetchCreators();
  };

  const triggerRefresh = async () => {
    await fetch("/api/refresh", { method: "POST" });
    fetchCreators();
  };

  return (
    <div className="p-4">
      <h2 className="text-lg font-bold mb-3">Tracked Creators</h2>

      <form onSubmit={addCreator} className="flex gap-2 mb-3">
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Instagram username"
          className="flex-1 px-3 py-1.5 border rounded text-sm dark:bg-gray-700 dark:border-gray-600"
        />
        <button
          type="submit"
          className="px-3 py-1.5 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
        >
          Add
        </button>
      </form>

      {error && <p className="text-red-500 text-xs mb-2">{error}</p>}

      <ul className="space-y-2 mb-3">
        {creators.map((c) => (
          <li
            key={c.id}
            className="flex items-center justify-between text-sm"
          >
            <span className="truncate">
              {c.display_name || c.username}
              {!c.is_active && (
                <span className="text-gray-400 ml-1">(inactive)</span>
              )}
            </span>
            <button
              onClick={() => removeCreator(c.id)}
              className="text-red-500 hover:text-red-700 text-xs ml-2"
            >
              Remove
            </button>
          </li>
        ))}
        {creators.length === 0 && (
          <li className="text-gray-400 text-xs">No creators tracked yet</li>
        )}
      </ul>

      <button
        onClick={triggerRefresh}
        className="w-full px-3 py-1.5 bg-green-500 text-white rounded text-sm hover:bg-green-600"
      >
        Refresh Now
      </button>
    </div>
  );
}
