import * as React from 'react';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';

import List from '@mui/material/List';

import SymptomsFilter from '../Filters/SymptomsFilter';
import CustomChip from '../IsolatedComponents/CustomChip';
import { Divider, Typography } from '@mui/material';
import FilterListIcon from '@mui/icons-material/FilterList';
import AnatomyFilter from '../Filters/AnatomyFilter';
import AgeFilter from '../Filters/AgeFilter';
import { getAnatomicalStructures, getPhenotypes } from '../../services/webService';

const drawerWidth = 350;

interface Props{
  children: React.ReactNode,
  updatePhenotypeFilterArray: (value: string, remove?: boolean)=>void
  updateAgeFilterArray: (value: string)=>void
  updateAnatomicFilterArray: (value: string)=>void
}

interface Item {
  value: string;
  label: string
}

export default function SidebarFilters({children, updatePhenotypeFilterArray, updateAnatomicFilterArray, updateAgeFilterArray}: Props) {

  const [symptoms, setSymptoms] = React.useState<string[]>([])
  const [symptomsItems, setSymptomsItems] = React.useState<Item[]>([])
  const [anatomyItems, setanatomyItems] = React.useState<Item[]>([])
  const [anatomySelection, setAnatomySelection] = React.useState<string[]>([])

  function updateSymptom(value: string){
    const aux = [...symptoms, value]
    setSymptoms(aux)
  }

  function updateSelection(value: string){
    const aux = [...anatomySelection, value]
    setAnatomySelection(aux)
  }

  function removeSymptom(value: string){
    const aux = [...symptoms]
    const index = aux.indexOf(value)
    aux.splice(index,1)
    setSymptoms(aux)
    const auxItem = symptomsItems.find((item)=>item.label === value)
    updatePhenotypeFilterArray(auxItem?.value, true)
  }

  function removeSelection(value: string){
    const aux = [...anatomySelection]
    const index = aux.indexOf(value)
    aux.splice(index,1)
    setAnatomySelection(aux)
    const auxItem = anatomyItems.find((item)=>item.label === value)
    updatePhenotypeFilterArray(auxItem?.value, true)
  }

  React.useEffect(()=>{
    async function setFilters(){
      const response = await getPhenotypes()
      setSymptomsItems(response)
      const res = await getAnatomicalStructures()
      setanatomyItems(res)
    } 
    setFilters()
  },[])

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
          <SymptomsFilter updateSymptom={updateSymptom} updateFilterArray={updatePhenotypeFilterArray}/>
        </Box>
        <Box sx={{display: 'flex', justifyContent: 'flex-start'}}>
        <List>
          {symptoms.map((text, index) => (
            <CustomChip text={text} key={index} removeFunction={removeSymptom} />
          ))}
        </List>
        </Box>
          <Divider sx={{mt: 4}}/>
        <Box sx={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
          <Typography variant='h6' sx={{marginY: 2}} >
            Anatomia
          </Typography>
          <AnatomyFilter updateSelection={updateSelection} updateAnatomicFilterArray={updateAnatomicFilterArray}/>
        </Box>
        <Box sx={{display: 'flex', justifyContent: 'flex-start'}}>
        <List>
          {anatomySelection.map((text, index) => (
            <CustomChip text={text} key={index} removeFunction={removeSelection}/>
          ))}
        </List>
        </Box>
        <Divider sx={{mt: 4}}/>
        <Box sx={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
          <Typography variant='h6' sx={{marginTop: 2}} >
            Rango Etario
          </Typography>
          <AgeFilter updateAgeFilterArray={updateAgeFilterArray} />
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
