import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import { Box, Button, Typography } from '@mui/material';
import ArrowForwardIosIcon from '@mui/icons-material/ArrowForwardIos';
import { Link } from 'react-router-dom';
import TiredPc from '../../assets/tired-pc.jpg'
import { useEffect, useState } from 'react';
import { getDiseasesByFilters } from '../../services/webService';


function getIdFromUrl(url: string){
  const auxString = url.split('/')
  return auxString[auxString.length -1]
}

interface Props {
  phenotype_ids: Array<string>;
  anatomical_ids: Array<string>;
  age_onset_ids: Array<string>;
}

export default function BasicTable({phenotype_ids, anatomical_ids, age_onset_ids}: Props) {
  const [rows, setRows] = useState([])
  
  useEffect(()=>{
    async function updateTable(){
      console.log(`Pheno: ${phenotype_ids}`)
      const response = await getDiseasesByFilters(phenotype_ids, anatomical_ids, age_onset_ids);
      setRows(response)
    }
     updateTable()    
  },[phenotype_ids, anatomical_ids, age_onset_ids])

  return (
    <Paper sx={{margin: 2, padding:4, borderRadius: 2,}}>
            <Box sx={{display: 'flex', justifyContent: 'center'}}>
        <Typography variant="h4" sx={{marginBottom: 2}}>
          Enfermedades
        </Typography>
      </Box>
      <Box sx={{border:1, borderColor: '#1d8bf8', borderRadius:2, padding:2}}>
        {
          rows.length === 0
          ? 
          <Box sx= {{ display: 'flex', justifyContent: 'center', height: '500', alignItems: 'center', flexDirection: 'column'}}>
            <Typography color={'#bcbcbc'} variant='h5' sx={{marginBottom: 4}}>
              Ninguna enfermedad corresponde a los sintomas seleccionados.
            </Typography>
            <Typography color={'#bcbcbc'} variant='h5' sx={{marginBottom: 4}}>
              Por favor modifique los filtros.
            </Typography>
            <img src={TiredPc} alt="Tired Pc" height={200}/>
          </Box>
          :
        <Table sx={{ minWidth: 650 }} aria-label="simple table">
          <TableHead>
            <TableRow>
              <TableCell align='center'>Enfermedad</TableCell>
              <TableCell align="center">Link</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row) => (
              <TableRow
                key={row.name}
                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
              >
                <TableCell component="th" scope="row" align='center'>
                  {row.name}
                </TableCell>
                <TableCell align="center">
                  <Link to={'/main/' + getIdFromUrl(row.id)}>
                    <Button variant='contained' endIcon={<ArrowForwardIosIcon/>}>
                      Ver
                    </Button>
                  </Link>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        }
      </Box>
    </Paper>
  );
}