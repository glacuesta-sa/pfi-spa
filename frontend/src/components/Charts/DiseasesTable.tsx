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

function createData(
  name: string,
  calories: number,
  fat: number,
  carbs: number,
  protein: number,
) {
  return { name, calories, fat, carbs, protein };
}

const rows = [
  createData('Frozen yoghurt', 159, 6.0, 24, 4.0),
  createData('Ice cream sandwich', 237, 9.0, 37, 4.3),
  createData('Eclair', 262, 16.0, 24, 6.0),
  createData('Cupcake', 305, 3.7, 67, 4.3),
  createData('Gingerbread', 356, 16.0, 49, 3.9),
];

export default function BasicTable() {
  return (

    <Paper sx={{margin: 2, padding:4, borderRadius: 2,}}>
            <Box sx={{display: 'flex', justifyContent: 'center'}}>
        <Typography variant="h4" sx={{marginBottom: 2}}>
          Enfermedades
        </Typography>
      </Box>
      <Box sx={{border:1, borderColor: '#1d8bf8', borderRadius:2, padding:2}}>
        {
          rows.length > 12
          ? 
          <Box sx= {{ display: 'flex', justifyContent: 'center', height: '500', alignItems: 'center', flexDirection: 'column'}}>
            <Typography color={'#bcbcbc'} variant='h5' sx={{marginBottom: 4}}>
              Demasiadas enfermedades corresponden a los sintomas seleccionados.
            </Typography>
            <Typography color={'#bcbcbc'} variant='h5' sx={{marginBottom: 4}}>
              Por favor agrega más filtros.
            </Typography>
            <img src={TiredPc} alt="Tired Pc" height={200}/>
          </Box>
          :
        <Table sx={{ minWidth: 650 }} aria-label="simple table">
          <TableHead>
            <TableRow>
              <TableCell align='center'>Dessert (100g serving)</TableCell>
              <TableCell align="center">Calories</TableCell>
              <TableCell align="center">Fat&nbsp;(g)</TableCell>
              <TableCell align="center">Carbs&nbsp;(g)</TableCell>
              <TableCell align="center">Protein&nbsp;(g)</TableCell>
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
                <TableCell align="center">{row.calories}</TableCell>
                <TableCell align="center">{row.fat}</TableCell>
                <TableCell align="center">{row.carbs}</TableCell>
                <TableCell align="center">{row.protein}</TableCell>
                <TableCell align="center">
                  <Link to={'/main/' + 'MONDO_0043786'}>
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