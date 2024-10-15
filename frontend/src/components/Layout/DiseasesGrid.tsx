import { Box, Container, Grid, Paper, Typography,  } from "@mui/material";
import DiseaseCard from "../IsolatedComponents/DiseaseCard";
import { useEffect, useState } from "react";
import { getDiseasesByFilters } from "../../services/webService";
import TiredPc from '../../assets/tired-pc.jpg'

interface Props {
    phenotype_ids: Array<string>;
    anatomical_ids: Array<string>;
    age_onset_ids: Array<string>;
  }
  
  interface IRow {
    name: string,
    id: string,
    description: string
    phenotypes: [Filter]
    multimedia: [string]
    age_onsets: [Filter]
    anatomical_structures: [Filter]
}

interface Filter{
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
        // @ts-ignore
        <Container maxWidth>
            {
                rows.length === 0
                ? 
                <Paper sx={{margin: 2, padding:4, borderRadius: 2, height:750}}>
                <Box sx={{border:1, borderColor: '#1d8bf8', borderRadius:2, padding:2,height:700}}>
                <Box sx= {{ display: 'flex', justifyContent: 'center', height: '500', alignItems: 'center', flexDirection: 'column'}}>
                    <Typography color={'#bcbcbc'} variant='h5' sx={{marginBottom: 4}}>
                    Ninguna enfermedad corresponde a los sintomas seleccionados.
                    </Typography>
                    <Typography color={'#bcbcbc'} variant='h5' sx={{marginBottom: 4}}>
                    Por favor modifique los filtros.
                    </Typography>
                    <img src={TiredPc} alt="Tired Pc" height={200}/>
                </Box>
                </Box>
                </Paper>
                :
                <Grid sx={{ flexGrow: 1 }} container spacing={2}>
                    <Grid item xs={12}>
                        <Grid container spacing={2} sx={{ justifyContent: 'flex-start' }}>
                            {rows.map((row) => (
                                <Grid key={row.id} item>
                                    <DiseaseCard media={row.multimedia[0]} id={row.id} diseaseTitle={row.name} description={row.description} anatomy={row.anatomical_structures} ageOnSet={row.age_onsets} phenotypes={row.phenotypes} />
                                </Grid>
                            ))}
                        </Grid>
                    </Grid>
                </Grid>
            }
        </Container>
    )
}