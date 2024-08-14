import { Box } from "@mui/material";
import CustomAppBar from "../components/Layout/Appbar";
import SidebarFilters from "../components/Layout/SidebarFilters";
import DiseasesTable from '../components/Charts/DiseasesTable'
import { useState } from "react";
export default function HomePage(){

    const [phenotypeIds, setPhenotypeIds] = useState<Array<string>>([])
    const [anatomicalIds, setAnatomical] = useState<Array<string>>([])
    const [ageIds, setAge] = useState<Array<string>>([])

    function updatePhenotypeFilterArray(value: string, remove?: boolean){
        if(remove){
            const aux = [...phenotypeIds]
            const index = aux.indexOf(value)
            aux.splice(index,1)
            setPhenotypeIds(aux)
        }else {
            const aux = [...phenotypeIds, value]
            setPhenotypeIds(aux)
        }
    }

    function updateAnatomicFilterArray(value: string, remove?: boolean){
        if(remove){

        }else {
            const aux = [...anatomicalIds, value]
            setAnatomical(aux)
        }
    }

    function updateAgeFilterArray(value: string){
        const aux = [...ageIds, value]
        setAge(aux)
    }    

    return(
        <>
            <CustomAppBar/>
            <SidebarFilters 
                updatePhenotypeFilterArray={updatePhenotypeFilterArray} 
                updateAgeFilterArray={updateAgeFilterArray} 
                updateAnatomicFilterArray={updateAnatomicFilterArray}
            >
                <Box>
                    <DiseasesTable age_onset_ids={ageIds} anatomical_ids={anatomicalIds} phenotype_ids={phenotypeIds} />
                </Box>
            </SidebarFilters>
        </>
    )
}