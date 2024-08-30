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
    try{
      const aux = props.data.map(element => element[0]);
      let uniqueArray = [...new Set(aux)];
      const auxData = []
      props.data.forEach(element => {
        const auxIndex = uniqueArray.indexOf(element[0])
        if (auxIndex !== -1) {
          auxData.push(element)
          uniqueArray.splice(auxIndex, 1);
        }
      });
      setChartData(auxData)
    }catch(error){
      console.log('Error TREE: ', error)
    }
  },[props])

  const [loading, setLoading] = useState(true)
  const [chartData, setChartData] = useState([])

  console.log("Chart data filtered", chartData)
  console.log("Chart data", props.data)

  return (
    <Paper sx={{margin: 2, padding:2, borderRadius: 2, width: '50%'}}>
      <Box sx={{display: 'flex', justifyContent: 'center'}}>
        <Typography variant="h4" sx={{marginBottom: 2}}>
          Mapa de Calor
        </Typography>
      </Box>
      <Box sx={{margin: 2, padding:2, borderRadius: 2, border:1, borderColor:'#1d8bf8'}}>
        {
              chartData.length === 0
              ? <Box sx={{height:"400px", display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
                  <PulseLoader size={20} color="#1d8bf8" />
              </Box>
              :
              <Chart
                chartType="TreeMap"
                width="100%"
                height="400px"
                data={chartData}
                options={options}
              />
        }
      </Box>
    </Paper>
  );
}
