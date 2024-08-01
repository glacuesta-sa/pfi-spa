import * as React from 'react';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';

import List from '@mui/material/List';

import SymptomsFilter from '../Filters/SymptomsFilter';
import CustomChip from '../IsolatedComponents/CustomChip';
import { Divider, Typography } from '@mui/material';
import FilterListIcon from '@mui/icons-material/FilterList';
import SexFilter from '../Filters/SexFilter';
import AnatomyFilter from '../Filters/AnatomyFilter';
import AgeFilter from '../Filters/AgeFilter';

const drawerWidth = 350;

export default function Sidebar({children}: {children: React.ReactNode}) {

  const [symptoms, setSymptoms] = React.useState<string[]>([])
  const [anatomySelection, setAnatomySelection] = React.useState<string[]>([])

  function updateSymptom(value: string){
    const aux = [...symptoms, value]
    setSymptoms(aux)
  }

  function updateSelection(value: string){
    const aux = [...anatomySelection, value]
    setAnatomySelection(aux)
  }

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
            Filtros
          </Typography>
        </Box>
        <Divider/>
        <Box sx={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
          <Typography variant='h6' sx={{marginY: 2}} >
            Sintomas
          </Typography>
          <SymptomsFilter updateSymptom={updateSymptom}/>
        </Box>
        <Box sx={{display: 'flex', justifyContent: 'flex-start'}}>
        <List>
          {symptoms.map((text, index) => (
            <CustomChip text={text} key={index}/>
          ))}
        </List>
        </Box>
          <Divider sx={{mt: 4}}/>
        <Box sx={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
          <Typography variant='h6' sx={{marginY: 2}} >
            Anatomia
          </Typography>
          <AnatomyFilter updateSelection={updateSelection}/>
        </Box>
        <Box sx={{display: 'flex', justifyContent: 'flex-start'}}>
        <List>
          {anatomySelection.map((text, index) => (
            <CustomChip text={text} key={index}/>
          ))}
        </List>
        </Box>
          <Divider sx={{mt: 4}}/>
        <Box sx={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
          <Typography variant='h6' sx={{marginTop: 2}} >
            Sexo
          </Typography>
          <SexFilter />
        </Box>
        <Divider sx={{mt: 4}}/>
        <Box sx={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
          <Typography variant='h6' sx={{marginTop: 2}} >
            Rango Etario
          </Typography>
          <AgeFilter />
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
