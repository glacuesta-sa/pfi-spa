import * as React from 'react';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import { Box, Button, List, ListItem, Paper } from '@mui/material';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import { PulseLoader } from 'react-spinners';
import { Link, useParams } from 'react-router-dom';
import { getDiseaseById } from '../../services/webService';


export default function InfoCard() {

  const {diseaseId} = useParams()
  const [title, setTitle] = React.useState('')
  const [description, setDescription] = React.useState('')
  const [causes, setCauses] = React.useState([])

  React.useEffect(()=>{
      async function getDisease(id:string){
        const response = await getDiseaseById(id)

        setTitle(response.name)
        setDescription(response.description)
        setCauses(response.causes)

      }
      getDisease(diseaseId)
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
                {title}
              <Divider />
              </Typography>
              <Typography paragraph align='justify'>
              {description}
              </Typography>
              <Typography variant="h6" gutterBottom>
                Causas
              </Typography>
              <List sx={{ listStyleType: 'disc' }}>
                {
                  causes.map((item)=>(
                <ListItem sx={{ display: 'list-item', ml:4 }}>
                  <Typography>
                    {item}
                  </Typography>
                </ListItem>

                  ))
                }
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