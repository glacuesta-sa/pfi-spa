import { Box } from "@mui/material";
import CustomAppBar from "../components/Layout/Appbar";
import Sidebar from "../components/Layout/Sidebar";
import DiseasesTable from '../components/Charts/DiseasesTable'
import { useState } from "react";
export default function HomePage(){

    const [phenotypeIds, setPhenotypeIds] = useState<Array<string>>([])
    const [anatomicalIds, setAnatomical] = useState<Array<string>>([])
    const [ageIds, setAge] = useState<Array<string>>([])

    function updatePhenotypeFilterArray(value: string){
        const aux = [...phenotypeIds, value]
        setPhenotypeIds(aux)
    }
    

    return(
        <>
            <CustomAppBar/>
            <Sidebar updatePhenotypeFilterArray={updatePhenotypeFilterArray}>
                <Box>
                    <DiseasesTable age_onset_ids={ageIds} anatomical_ids={anatomicalIds} phenotype_ids={phenotypeIds} />
                </Box>
            </Sidebar>
        </>
    )
}