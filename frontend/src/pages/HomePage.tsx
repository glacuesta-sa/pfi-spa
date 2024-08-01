import { Box } from "@mui/material";
import CustomAppBar from "../components/Layout/Appbar";
import Sidebar from "../components/Layout/Sidebar";
import DiseasesTable from '../components/Charts/DiseasesTable'
export default function HomePage(){
    return(
        <>
            <CustomAppBar/>
            <Sidebar>
                <Box>
                    <DiseasesTable />
                </Box>
            </Sidebar>
        </>
    )
}