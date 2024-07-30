import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import LocalHospitalIcon from '@mui/icons-material/LocalHospital';


export default function CustomAppBar() {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="sticky">
        <Toolbar variant="dense">
          <Box sx={{display:'flex', flex: 1, justifyContent:'center', alignItems: 'center'}}>
            <Typography variant="h4" color="inherit" component="div" sx={{marginRight:2}}>
              Sintomatologia ORG
            </Typography>
            <LocalHospitalIcon fontSize='large'/>
          </Box>
        </Toolbar>
      </AppBar>
    </Box>
  );
}