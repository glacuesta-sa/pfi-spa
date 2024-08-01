import * as React from 'react';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import { Box, Button, List, ListItem, Paper } from '@mui/material';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import { PulseLoader } from 'react-spinners';
import { Link } from 'react-router-dom';


export default function InfoCard() {

    React.useEffect(()=>{
      setTimeout(
          ()=>setLoading(false),
          2000
      )
  },[])

  const [loading, setLoading] = React.useState(true)

  return (
    <Paper sx={{margin: 2, padding:2, borderRadius: 2, width: '50%'}}>
       {
        loading
        ? <Box sx={{height:"400px", display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
            <PulseLoader size={20} color="#1d8bf8" />
        </Box>
        :
        
          <Grid
            item
            xs={12}
            md={8}
            sx={{
              '& .markdown': {
                py: 3,
              },
            }}
          >
              <Typography variant="h5" gutterBottom>
                Epilepsia de Lóbulo Frontal Tipo 1
              <Divider />
              </Typography>
              <Typography paragraph align='justify'>
              Las convulsiones del lóbulo frontal son un tipo frecuente de epilepsia. La epilepsia es un trastorno del cerebro en el que grupos de neuronas cerebrales envían una descarga de señales eléctricas.
              </Typography>
                
              <Typography paragraph align='justify'>
                Estas convulsiones comienzan en la parte delantera del cerebro, que es la zona llamada lóbulo frontal.
                El lóbulo frontal es grande y tiene funciones importantes. Por este motivo, las convulsiones del lóbulo frontal quizás ocasionen síntomas inusuales y pueden parecer relacionados con una enfermedad mental. Además, las convulsiones pueden confundirse con un trastorno del sueño, ya que suelen ocurrir mientras se duerme. Este tipo de convulsiones también reciben el nombre de epilepsia del lóbulo frontal.
              </Typography>
              <Typography variant="h6" gutterBottom>
                Causas
              </Typography>
              <List sx={{ listStyleType: 'disc' }}>
                <ListItem sx={{ display: 'list-item', ml:4 }}>
                  <Typography>
                    Antecedentes familiares de convulsiones o trastornos cerebrales.
                  </Typography>
                </ListItem>
                <ListItem sx={{ display: 'list-item', ml:4 }}>
                  <Typography>
                  Infección en el cerebro.
                  </Typography>
                </ListItem>
                <ListItem sx={{ display: 'list-item', ml:4 }}>
                  <Typography>
                  Vasos sanguíneos o tejidos del cerebro que se forman de manera irregular.
                  </Typography>
                </ListItem>
              </List>
              <Box sx={{display:'flex', justifyContent: 'center'}}>
              <Link to="/treatment">
              <Button variant='contained' endIcon={<ArrowForwardIcon />}>
                Tratmiento Sugerido
              </Button>
              </Link>
              </Box>
          </Grid>
        }
    </Paper>
  );
}