import { BrowserRouter, Route, Routes } from "react-router-dom";
import MainDiseasePage from "./pages/MainDiseasePage";
import HomePage from "./pages/HomePage";
import TreatmentPage from "./pages/TreatmentPage";


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/main" element={<MainDiseasePage />} />
        <Route path="/treatment" element={<TreatmentPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
