import AppHeader from "./AppHeader";
import NavSidebar from "./NavSidebar";
import Footer from "./Footer";

export default function MainLayout({ children }) {
  return (
    <div className="app-layout">
      <AppHeader />
      <div className="app-body">
        <NavSidebar />
        <main className="main-content">
          {children}
        </main>
      </div>
      <Footer />
    </div>
  );
}
