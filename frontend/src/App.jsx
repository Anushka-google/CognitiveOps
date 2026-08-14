import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";

import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import WorkflowExplorer from "./pages/WorkflowExplorer";

function App() {
  return (
    <BrowserRouter>

      <Routes>

        {/* Landing / Home Page */}
        <Route
          path="/"
          element={<Home />}
        />

        {/* Existing Dashboard */}
        <Route
          path="/dashboard"
          element={<Dashboard />}
        />

        {/* Workflow Explorer */}
        <Route
          path="/workflow"
          element={<WorkflowExplorer />}
        />

      </Routes>

    </BrowserRouter>
  );
}

export default App;