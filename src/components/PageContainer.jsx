export default function PageContainer({ title, subtitle, children }) {
  return (
    <div className="page-container">
      <div className="page-header">
        <h2 className="page-title">{title}</h2>
        {subtitle && <p className="page-subtitle">{subtitle}</p>}
      </div>
      <div className="page-content">
        {children}
      </div>
    </div>
  );
}
