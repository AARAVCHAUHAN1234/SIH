import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

function Dashboard() {
  return <h1>Garuda Kavach Dashboard</h1>;
}

function Bridges() {
  return <h1>Bridges</h1>;
}

function BridgeDetails() {
  return <h1>Bridge Details</h1>;
}

function InspectionDetails() {
  return <h1>Inspection Details</h1>;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/bridges" element={<Bridges />} />
        <Route
          path="/bridges/:bridgeId"
          element={<BridgeDetails />}
        />
        <Route
          path="/inspections/:inspectionId"
          element={<InspectionDetails />}
        />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;