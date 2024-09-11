import * as React from 'react';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import { Button, Divider, Typography } from '@mui/material';
import FilterListIcon from '@mui/icons-material/FilterList';
import RelationshipTypeFilter from '../Filters/RelationshipTypeFilter';
import { postPrediction } from '../../services/webService';

const drawerWidth = 350;

interface Props{
  children: React.ReactNode,
  diseaseId: string
}

interface Item{
  value?: string,
  label?: string
}


const postPredictionForSelection = (diseaseId: string, property: string) =>{
  console.log('Calling predict')
  try{
    postPrediction(diseaseId, property)
  } catch(error){
    console.log('Error in post prediction: ', error)
  }
}

export default function SidebarDisease({children, diseaseId}: Props) {

  const [selection, setSelection] = React.useState<Item>({label: undefined, value: undefined})

  

  return (
    <Box sx={{ display: 'flex'}}>
      <Drawer
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            borderRadius:4,
            height: '90%',
            padding:2,
            boxSizing: 'border-box',
            marginY:11,
            marginX:2,
            boxShadow:2,
          },
        }}
        variant="permanent"
        anchor="left"
      >
        <Box sx={{display: 'flex', justifyContent: 'center', alignItems:'center' ,marginBottom: 2}}>
          <FilterListIcon />
          <Typography variant='h5' sx={{marginX: 2}} >
            Tipos de Relaciones
          </Typography>
        </Box>
        <Divider/>
        <Box sx={{display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent:'center'}}>
          <RelationshipTypeFilter setSelection={setSelection} />
        </Box>
        <Box sx={{display: 'flex', justifyContent: 'center', marginTop: 6}}>
          <Button disabled={selection?.value === undefined || selection?.value === null} variant='contained' color='warning' onClick={()=>postPredictionForSelection(diseaseId, selection?.value.split('/').at(-1))}>
            Predecir
          </Button>
        </Box>
      </Drawer>
      <Box
        component="main"
        sx={{ flexGrow: 1, bgcolor: '#efefef', p: 3 }}
      >
        {children}
      </Box>
    </Box>
  );
} 
