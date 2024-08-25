import { Box, Paper, Typography } from "@mui/material";
import { useEffect, useState } from "react";
import { Chart } from "react-google-charts";
import { PulseLoader } from "react-spinners";


export const options = {
  minColor: "red",
  midColor: "#ddd",
  maxColor: "#1976d2",
  headerHeight: 20,
  fontColor: "black",
  showScale: false,
};

export default function TreeMap(props) {
  
  useEffect(()=>{
    setTimeout(
        ()=>setLoading(false),
        2000
    )
  },[])

  const [loading, setLoading] = useState(true)

  return (
    <Paper sx={{margin: 2, padding:2, borderRadius: 2, width: '50%'}}>
      <Box sx={{display: 'flex', justifyContent: 'center'}}>
        <Typography variant="h4" sx={{marginBottom: 2}}>
          Mapa de Calor
        </Typography>
      </Box>
      <Box sx={{margin: 2, padding:2, borderRadius: 2, border:1, borderColor:'#1d8bf8'}}>
        {
              loading
              ? <Box sx={{height:"400px", display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
                  <PulseLoader size={20} color="#1d8bf8" />
              </Box>
              :
              <Chart
                chartType="TreeMap"
                width="100%"
                height="400px"
                data={props.data}
                options={options}
              />
        }
      </Box>
    </Paper>
  );
}
