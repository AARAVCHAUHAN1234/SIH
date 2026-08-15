import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import BridgeDetails from "./pages/BridgeDetails";
import InspectionDetails from "./pages/InspectionDetails";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />

        <Route
          path="/bridges/:bridgeId"
          element={<BridgeDetails />}
        />

        <Route
          path="/inspections/:inspectionId"
          element={<InspectionDetails />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;