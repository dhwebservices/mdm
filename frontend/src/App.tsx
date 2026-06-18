import { PortalLayout } from "./layout/PortalLayout";
import { Dashboard } from "./pages/Dashboard";

export function App() {
  return (
    <PortalLayout>
      <Dashboard />
    </PortalLayout>
  );
}
