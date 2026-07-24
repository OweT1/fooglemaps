import PageContainer from "../components/PageContainer";
import { useTheme } from "../context/ThemeContext";

export default function SettingsPage() {
  const { preference, setTheme } = useTheme();

  return (
    <PageContainer title="Settings" subtitle="Manage your preferences">
      <div className="settings-page">
        <section className="settings-section">
          <h3>Appearance</h3>
          <div className="settings-row">
            <label>Theme</label>
            <select value={preference} onChange={(e) => setTheme(e.target.value)}>
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="system">System</option>
            </select>
          </div>
        </section>
        <section className="settings-section">
          <h3>Map</h3>
          <div className="settings-row">
            <label>Default Zoom Level</label>
            <select defaultValue="12">
              <option value="10">10 (Far)</option>
              <option value="12">12 (Medium)</option>
              <option value="14">14 (Close)</option>
            </select>
          </div>
          <div className="settings-row">
            <label>Map Type</label>
            <select defaultValue="roadmap">
              <option value="roadmap">Roadmap</option>
              <option value="satellite">Satellite</option>
              <option value="hybrid">Hybrid</option>
              <option value="terrain">Terrain</option>
            </select>
          </div>
        </section>
        <section className="settings-section">
          <h3>Notifications</h3>
          <div className="settings-row">
            <label>New Food Spots</label>
            <input type="checkbox" defaultChecked />
          </div>
          <div className="settings-row">
            <label>Recommendations</label>
            <input type="checkbox" defaultChecked />
          </div>
        </section>
      </div>
    </PageContainer>
  );
}
