import * as React from 'react';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import SymptomsFilter from '../Filters/SymptomsFilter';
import CustomChip from '../IsolatedComponents/CustomChip';
import { Divider, Typography } from '@mui/material';
import FilterListIcon from '@mui/icons-material/FilterList';

const drawerWidth = 350;

interface Props{
  children: React.ReactNode

}

export default function SidebarDisease({children}: Props) {

  const [symptoms, setSymptoms] = React.useState<string[]>([])

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
        <Box sx={{display: 'flex', justifyContent: 'flex-start'}}>
        <List>
          {symptoms.map((text, index) => (
            <CustomChip text={text} key={index}/>
          ))}
        </List>
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
