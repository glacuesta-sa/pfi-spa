import { Box } from "@mui/material";
import Dendogram from "../components/Charts/Dendogram";
import CustomAppBar from "../components/Layout/Appbar";
import Sidebar from "../components/Layout/Sidebar";
import TreeMap from "../components/Charts/TreeMap";
import InfoCard from "../components/Charts/InfoCard";

export default function MainDiseasePage(){
    return(
        <>
            <CustomAppBar/>
            <Sidebar>
                <Dendogram />
                <Box sx={{display: 'flex'}}>
                    <TreeMap />
                    <InfoCard />
                </Box>
            </Sidebar>
        </>
    )
}