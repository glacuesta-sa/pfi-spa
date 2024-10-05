
import { Box, Paper, Typography } from "@mui/material";
import { useEffect, useState } from "react";
import { Chart } from "react-google-charts";
import { PulseLoader } from "react-spinners";
import DendogramLegend from "../IsolatedComponents/DendogramLegend";



const options = {
  colors: ["#1d8bf8", "#1d8bf8", "#1d8bf8"],
  wordtree: {
    format: "explicit",
    type: "suffix",
  },
};

interface Props {
  data: [] | undefined,
  loadingUpdate: boolean
}

export default function Dendogram({data, loadingUpdate}: Props) {

    useEffect(()=>{
        setTimeout(
            ()=>setLoading(false),
            2000
        )
    },[])

    const [loading, setLoading] = useState(true)

  return (
    <Paper sx={{margin: 2, padding:2, borderRadius: 2,}}>
      <Box sx={{display: 'flex', justifyContent: 'center'}}>
        <Typography variant="h4" sx={{marginBottom: 2}}>
          Diagnostico Estimativo
        </Typography>
      </Box>
      <DendogramLegend />
      <Box sx={{border:1, borderColor: '#1d8bf8', borderRadius:2, padding:2}}>
        {
            loading || loadingUpdate
            ? <Box sx={{height:"400px", display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
                <PulseLoader size={20} color="#1d8bf8" />
            </Box>
            :
            <Chart
                chartType="WordTree"
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
