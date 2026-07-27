import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export default function FeedPage() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetch("/api/posts?limit=50")
      .then((r) => r.json())
      .then((data) => setPosts(data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <p className="text-gray-500">Loading posts...</p>
      </div>
    );
  }

  if (posts.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <p className="text-gray-500">No posts yet. Add creators to get started.</p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-4">
      <h1 className="text-xl font-bold mb-4">Food Feed</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {posts.map((post) => (
          <div
            key={post.id}
            className="border rounded-lg overflow-hidden shadow-sm bg-white dark:bg-gray-800"
          >
            {post.image_url && (
              <img
                src={post.image_url}
                alt={post.caption || "Post image"}
                className="w-full h-48 object-cover"
                loading="lazy"
              />
            )}
            <div className="p-3">
              {post.location_name && (
                <p className="font-semibold text-sm">{post.location_name}</p>
              )}
              {post.caption && (
                <p className="text-xs text-gray-600 dark:text-gray-300 mt-1 line-clamp-2">
                  {post.caption}
                </p>
              )}
              <div className="flex gap-2 mt-2">
                {post.post_url && (
                  <a
                    href={post.post_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-500 hover:underline"
                  >
                    View on Instagram
                  </a>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
