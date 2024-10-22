import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import ApollodIcon from '../../assets/Apollod-no-title.jpg'
import { Avatar } from '@mui/material';



export default function CustomAppBar() {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="sticky">
        <Toolbar variant="dense">
          <Box sx={{display:'flex', flex: 1, justifyContent:'center', alignItems: 'center'}}>
            <Typography variant="h4" color="inherit" component="div" sx={{marginRight:2}}>
              APOLLOD
            </Typography>
            <Avatar src={ApollodIcon} sx={{ width: 50, height: 50, marginY: 0.5 }} />
          </Box>
        </Toolbar>
      </AppBar>
    </Box>
  );
}