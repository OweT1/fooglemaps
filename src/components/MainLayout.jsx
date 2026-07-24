import { Outlet } from "react-router-dom";
import AppHeader from "./AppHeader";
import NavSidebar from "./NavSidebar";
import Footer from "./Footer";

export default function MainLayout() {
  return (
    <div className="flex flex-col h-screen">
      <AppHeader />
      <div className="flex flex-1 pt-header min-h-0">
        <NavSidebar />
        <main className="flex-1 min-w-0 overflow-y-auto flex flex-col">
          <Outlet />
        </main>
      </div>
      <Footer />
    </div>
  );
}
