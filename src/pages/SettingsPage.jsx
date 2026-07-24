import PageContainer from "../components/PageContainer";
import { useTheme } from "../context/ThemeContext";

export default function SettingsPage() {
  const { preference, setTheme } = useTheme();

  return (
    <PageContainer title="Settings" subtitle="Manage your preferences">
      <div className="max-w-[480px] flex flex-col gap-6">
        <section className="border border-border rounded-lg p-5">
          <h3 className="text-[15px] font-semibold mb-4 pb-3 border-b border-border">Appearance</h3>
          <div className="flex items-center justify-between py-2 border-b border-border last:border-b-0">
            <label className="text-sm text-content">Theme</label>
            <select value={preference} onChange={(e) => setTheme(e.target.value)} className="border border-border rounded-sm px-2.5 py-1.5 bg-surface text-[13px] outline-none">
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="system">System</option>
            </select>
          </div>
        </section>
        <section className="border border-border rounded-lg p-5">
          <h3 className="text-[15px] font-semibold mb-4 pb-3 border-b border-border">Map</h3>
          <div className="flex items-center justify-between py-2 border-b border-border last:border-b-0">
            <label className="text-sm text-content">Default Zoom Level</label>
            <select defaultValue="12" className="border border-border rounded-sm px-2.5 py-1.5 bg-surface text-[13px] outline-none">
              <option value="10">10 (Far)</option>
              <option value="12">12 (Medium)</option>
              <option value="14">14 (Close)</option>
            </select>
          </div>
          <div className="flex items-center justify-between py-2 border-b border-border last:border-b-0">
            <label className="text-sm text-content">Map Type</label>
            <select defaultValue="roadmap" className="border border-border rounded-sm px-2.5 py-1.5 bg-surface text-[13px] outline-none">
              <option value="roadmap">Roadmap</option>
              <option value="satellite">Satellite</option>
              <option value="hybrid">Hybrid</option>
              <option value="terrain">Terrain</option>
            </select>
          </div>
        </section>
        <section className="border border-border rounded-lg p-5">
          <h3 className="text-[15px] font-semibold mb-4 pb-3 border-b border-border">Notifications</h3>
          <div className="flex items-center justify-between py-2 border-b border-border last:border-b-0">
            <label className="text-sm text-content">New Food Spots</label>
            <input type="checkbox" defaultChecked className="w-[18px] h-[18px] accent-primary" />
          </div>
          <div className="flex items-center justify-between py-2 border-b border-border last:border-b-0">
            <label className="text-sm text-content">Recommendations</label>
            <input type="checkbox" defaultChecked className="w-[18px] h-[18px] accent-primary" />
          </div>
        </section>
      </div>
    </PageContainer>
  );
}
