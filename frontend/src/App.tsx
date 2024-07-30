import { Box, } from "@mui/material";
import CustomAppBar from "./components/Layout/Appbar";
import Dendogram from "./components/Charts/Dendogram";
import TreeMap from "./components/Charts/TreeMap";
import Sidebar from "./components/Layout/Sidebar";
import InfoCard from "./components/IsolatedComponents/InfoCard";


function App() {
  return (
    <main>
      <CustomAppBar/>
      <Sidebar>
        <Dendogram />
        <Box sx={{display: 'flex'}}>
          <TreeMap />
          <InfoCard />
        </Box>
      </Sidebar>
    </main>
  );
}

export default App;
