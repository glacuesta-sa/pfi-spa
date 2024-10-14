import { Container, Grid,  } from "@mui/material";
import DiseaseCard from "../IsolatedComponents/DiseaseCard";
import { useEffect, useState } from "react";
import { getDiseasesByFilters } from "../../services/webService";

interface Props {
    phenotype_ids: Array<string>;
    anatomical_ids: Array<string>;
    age_onset_ids: Array<string>;
  }
  
  interface IRow {
    name: string,
    id: string,
    description: string
    phenotypes: [Phenotype]
}

interface Phenotype{
    label: string
}

export default function DiseasesGrid({phenotype_ids, anatomical_ids, age_onset_ids}: Props){

    const [rows, setRows] = useState<IRow[]>([])
  
    useEffect(()=>{
      async function updateTable(){
        const response = await getDiseasesByFilters(phenotype_ids, anatomical_ids, age_onset_ids);
        setRows(response)
      }
       updateTable()    
    },[phenotype_ids, anatomical_ids, age_onset_ids])

    return(
        <Container maxWidth>
            <Grid sx={{ flexGrow: 1 }} container spacing={2}>
                <Grid item xs={12}>
                    <Grid container spacing={2} sx={{ justifyContent: 'flex-start' }}>
                        {rows.map((row) => (
                            <Grid key={row.id} item>
                                <DiseaseCard diseaseTitle={row.name} description={row.description} phenotypes={row.phenotypes} />
                            </Grid>
                        ))}
                    </Grid>
                </Grid>
            </Grid>
        </Container>
    )
}