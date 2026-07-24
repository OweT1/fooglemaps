export default function PageContainer({ title, subtitle, children }) {
  return (
    <div className="p-6 flex-1 flex flex-col max-lg:p-4 max-sm:p-3">
      <div className="mb-6">
        <h2 className="text-[22px] font-bold">{title}</h2>
        {subtitle && <p className="mt-1 text-content-secondary text-sm">{subtitle}</p>}
      </div>
      <div className="flex-1">
        {children}
      </div>
    </div>
  );
}
