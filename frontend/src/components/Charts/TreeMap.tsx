import { Box, Paper, Typography } from "@mui/material";
import { useEffect, useState } from "react";
import { Chart } from "react-google-charts";
import { PulseLoader } from "react-spinners";

export const data = [
  [
    "Location",
    "Parent",
    "size",
    "color",
  ],
  ["Epilepsia", null, 0, 0],
  ["Generalizada", "Epilepsia", 0, 0],
  ["Focales", "Epilepsia", 0, 0],
  ["Infantil", "Epilepsia", 0, 0],
  ["Australia", "Epilepsia", 0, 0],
  ["De Ausencia", "Epilepsia", 0, 0],
  ["Brazil", "Generalizada", 11, 10],
  ["USA", "Generalizada", 52, 31],
  ["Mexico", "Generalizada", 24, 12],
  ["Canada", "Generalizada", 16, -23],
  ["Tonico Clonica", "Focales", 42, -11],
  ["Lobulo Frontal T1", "Focales", 31, -2],
  ["Parcial SImple", "Focales", 22, -13],
  ["Lobulo Frontal T3", "Focales", 17, 4],
  ["Lobulo Frontal T2", "Focales", 21, -5],
  ["China", "Infantil", 36, 4],
  ["Japan", "Infantil", 20, -12],
  ["India", "Infantil", 40, 63],
  ["Laos", "Infantil", 4, 34],
  ["Mongolia", "Infantil", 1, -5],
  ["Israel", "Infantil", 12, 24],
  ["Iran", "Infantil", 18, 13],
  ["Pakistan", "Infantil", 11, -52],
  ["Egypt", "De Ausencia", 21, 0],
  ["S. De Ausencia", "De Ausencia", 30, 43],
  ["Sudan", "De Ausencia", 12, 2],
  ["Congo", "De Ausencia", 10, 12],
  ["Zaire", "De Ausencia", 8, 10],
];

export const options = {
  minColor: "red",
  midColor: "#ddd",
  maxColor: "#1976d2",
  headerHeight: 20,
  fontColor: "black",
  showScale: false,
};

export default function TreeMap() {
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
                data={data}
                options={options}
              />
        }
      </Box>
    </Paper>
  );
}
