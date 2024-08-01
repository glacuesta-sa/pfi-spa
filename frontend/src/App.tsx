import { BrowserRouter, Route, Routes } from "react-router-dom";
import MainDiseasePage from "./pages/MainDiseasePage";
import HomePage from "./pages/HomePage";


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/main">
          <Route path=":diseaseId" element={<MainDiseasePage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
