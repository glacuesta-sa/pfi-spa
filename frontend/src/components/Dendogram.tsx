
import { Box, Paper, Typography } from "@mui/material";
import { Chart } from "react-google-charts";


export const data = [
    [
        "id",
        "childLabel",
        "parent",
        "size",
        {
            "role": "style"
        }
    ],
    [
        0,
        "frontal lobe epilepsy",
        -1,
        1,
        "#1d8bf8"
    ],
    [
        1,
        "sleep-related hypermotor epilepsy",
        0,
        1,
        "#1d8bf8"
    ],
    [
        2,
        "autosomal dominant nocturnal frontal lobe epilepsy 1",
        1,
        1,
        "#1d8bf8"
    ],
    [
        3,
        "autosomal dominant nocturnal frontal lobe epilepsy 2",
        1,
        1,
        "#1d8bf8"
    ],
    [
        4,
        "autosomal dominant nocturnal frontal lobe epilepsy 3",
        1,
        1,
        "#1d8bf8"
    ],
    [
        5,
        "autosomal dominant nocturnal frontal lobe epilepsy 4",
        1,
        1,
        "#1d8bf8"
    ],
    [
        6,
        "autosomal dominant nocturnal frontal lobe epilepsy 5",
        1,
        1,
        "#1d8bf8"
    ],
    [
        7,
        "autosomal dominant nocturnal frontal lobe epilepsy",
        0,
        1,
        "#1d8bf8"
    ],
    [
        8,
        "autosomal dominant nocturnal frontal lobe epilepsy 1",
        7,
        1,
        "#1d8bf8"
    ],
    [
        9,
        "autosomal dominant nocturnal frontal lobe epilepsy 2",
        7,
        1,
        "#1d8bf8"
    ],
    [
        10,
        "autosomal dominant nocturnal frontal lobe epilepsy 3",
        7,
        1,
        "#1d8bf8"
    ],
    [
        11,
        "autosomal dominant nocturnal frontal lobe epilepsy 4",
        7,
        1,
        "#1d8bf8"
    ],
    [
        12,
        "autosomal dominant nocturnal frontal lobe epilepsy 5",
        7,
        1,
        "#1d8bf8"
    ],
    [
        13,
        "primary motor cortex epilepsy",
        0,
        1,
        "#1d8bf8"
    ]
]

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
