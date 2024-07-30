
import { Box, Container, Paper } from "@mui/material";
import CustomAppBar from "./components/Appbar";
import Dendogram from "./components/Dendogram";
import TreeMap from "./components/TreeMap";
import Sidebar from "./components/Sidebar";
import InfoCard from "./components/InfoCard";


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
