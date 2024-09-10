import { Box, Paper, Typography } from "@mui/material";
import { useEffect, useState } from "react";
import { Chart } from "react-google-charts";
import { PulseLoader } from "react-spinners";


const options = {
  minColor: "red",
  midColor: "#ddd",
  maxColor: "#1976d2",
  headerHeight: 20,
  fontColor: "black",
  showScale: false,
};

interface Props {
  data: any[] | undefined
}

export default function TreeMap({data}: Props) {
  
  useEffect(()=>{    
    try{
      // @ts-expect-error unable to type array of arrays
      const aux = data.map(element => element[0]);
      const uniqueArray = [...new Set(aux)];
      const auxData: string[] = []
      // @ts-expect-error unable to type array of arrays
      data.forEach(element => {
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
  },[data])

  const [chartData, setChartData] = useState<string[]>([])


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
