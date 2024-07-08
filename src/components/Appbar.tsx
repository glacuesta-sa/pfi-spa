import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';

export default function CustomAppBar() {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar variant="dense">
          <Box sx={{display:'flex', flex: 1, justifyContent:'center'}}>
          <Typography variant="h6" color="inherit" component="div">
            Sintomatologia ORG
          </Typography>
          </Box>
        </Toolbar>
      </AppBar>
    </Box>
  );
}