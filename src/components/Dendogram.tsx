
import { Box, Paper, Typography } from "@mui/material";
import { Chart } from "react-google-charts";


export const data = [
  ["id", "childLabel", "parent", "size", { role: "style" }],
  [0, "Epilepsia", -1, 1, "#1d8bf8"],
  [1, "Generalizadas", 0, 1, "#1d8bf8"],
  [2, "Focales", 0, 5, "#1d8bf8"],
  [3, "Epilepsia Infantil", 0, 1, "red"],
  [4, "De Ausencia", 1, 1, "red"],
  [5, "Mioclonica", 1, 1, "red"],
  [6, "Atonica", 1, 1, "red"],
  [10, "Parciales Simple", 2, 1, "red"],
  [11, "Parciales Complejas", 2, 1, "orange"],
  [12, "Lobulo Frontal", 2, 5, "#1d8bf8"],
  [13, "Tónico-Clónica", 2, 1, "orange"],
  [15, "Tipo 1", 12, 5, "#1d8bf8"],
  [16, "Tipo 2", 12, 2, "orange"],
  [17, "Tipo 3", 12, 2, "orange"],
];

export const options = {
  colors: ["#1d8bf8", "#1d8bf8", "#1d8bf8"],
  wordtree: {
    format: "explicit",
    type: "suffix",
  },
};

export default function Dendogram() {
  return (
    <Paper sx={{margin: 2, padding:2, borderRadius: 2,}}>
      <Box sx={{display: 'flex', justifyContent: 'center'}}>
        <Typography variant="h4" sx={{marginBottom: 2}}>
          Diagnostico Estimativo
        </Typography>
      </Box>
      <Box sx={{border:1, borderColor: '#1d8bf8', borderRadius:2, padding:2}}>
    <Chart
      chartType="WordTree"
      width="100%"
      height="400px"
      data={data}
      options={options}
    />
    </Box>
    </Paper>
  );
}
