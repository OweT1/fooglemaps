export default function Footer() {
  return (
    <footer className="app-footer">
      <span>&copy; {new Date().getFullYear()} Fooglemaps</span>
      <span className="footer-links">
        <a href="#privacy">Privacy</a>
        <a href="#terms">Terms</a>
      </span>
    </footer>
  );
}
