import { Box, Typography } from "@mui/material";
import FiberManualRecordIcon from '@mui/icons-material/FiberManualRecord';

const legends: Legend[] =[
    {label: "Anatomical Structure", color: "error"},
    {label: "Chemical", color:"success"},
    // @ts-expect-error color not typed
    {label: "Disease", color:"#0a0a0a"},
    {label: "Exposure", color:"primary"},
    {label: "Phenotype", color:"secondary"},
    {label: "Predicted", color:"warning"},
    {label: "Treatment", color:"info"},
]

interface Legend {
    label: string,
    color: "inherit" | "disabled" | "error" | "primary" | "secondary" | "info" | "success" | "warning" | "action"
}

export default function DendogramLegend(){
    return(
        <Box sx={{display: 'flex', marginBottom: 2}}>
            {
                legends.map((item)=>(
                    <>
                        <FiberManualRecordIcon color={item.color} sx={{marginRight: 1}} />
                        <Typography sx={{marginRight: 6}}>
                            {item.label}
                        </Typography>
                    </>
                ))
            }
        </Box>
    )
}