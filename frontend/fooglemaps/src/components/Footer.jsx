export default function Footer() {
  return (
    <footer className="h-footer flex items-center justify-between px-6 border-t border-border text-xs text-content-muted flex-shrink-0">
      <span>&copy; {new Date().getFullYear()} Fooglemaps</span>
      <span className="flex gap-4">
        <a href="#privacy" className="hover:text-content-secondary">Privacy</a>
        <a href="#terms" className="hover:text-content-secondary">Terms</a>
      </span>
    </footer>
  );
}
