import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function AvatarIcon({ size = 20 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
    >
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
      <circle cx="12" cy="7" r="4" />
    </svg>
  );
}

export default function UserMenu() {
  const { user, signIn, signOut } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [imgError, setImgError] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    const handler = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target))
        setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  useEffect(() => {
    setImgError(false);
  }, [user?.picture]);

  if (!user) {
    return (
      <button className="signin-btn" onClick={signIn}>
        Sign in
      </button>
    );
  }

  function userPicture(userPicture) {
    return (
      <img
        src={userPicture}
        alt=""
        className="user-avatar-img"
        onError={() => setImgError(true)}
      />
    );
  }
  return (
    <div className="user-menu" ref={menuRef}>
      <button
        className="user-menu-trigger"
        onClick={() => setOpen((o) => !o)}
        aria-label="User menu"
      >
        {user.picture && !imgError ? (
          userPicture(user.picture)
        ) : (
          <AvatarIcon size={20} />
        )}
      </button>
      {open && (
        <div className="user-menu-dropdown">
          <div className="user-menu-header">
            {user.picture && !imgError ? (
              userPicture(user.picture)
            ) : (
              <div className="user-menu-avatar flex items-center justify-center bg-surface-tertiary text-content-secondary">
                <AvatarIcon size={20} />
              </div>
            )}
            <div>
              <p className="user-menu-name">{user.name}</p>
              <p className="user-menu-email">{user.email}</p>
            </div>
          </div>
          <div className="user-menu-items">
            <button
              onClick={() => {
                setOpen(false);
                navigate("/saved");
              }}
            >
              Saved Places
            </button>
            <button
              onClick={() => {
                setOpen(false);
                navigate("/settings");
              }}
            >
              Settings
            </button>
          </div>
          <div className="user-menu-footer">
            <button
              onClick={() => {
                setOpen(false);
                signOut();
              }}
            >
              Sign out
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
