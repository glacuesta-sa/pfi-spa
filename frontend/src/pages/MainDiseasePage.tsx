import { Box } from "@mui/material";
import Dendogram from "../components/Charts/Dendogram";
import CustomAppBar from "../components/Layout/Appbar";
import Sidebar from "../components/Layout/Sidebar";
import TreeMap from "../components/Charts/TreeMap";
import InfoCard from "../components/Charts/InfoCard";
import { useState, useEffect } from "react";
import { getChartsData } from "../services/webService";
import { useParams } from "react-router-dom";

export default function MainDiseasePage(){

    const {diseaseId} = useParams()

    const [dendogramData, setDendogramData] = useState()
    const [heatMapData, setHeatMapData] = useState()

    useEffect(()=>{
        async function setDiseaseData(){
          const response = await getChartsData(diseaseId)
          console.log(`Response charts: ${JSON.stringify(response)}`)
          const auxDendogram = []
          const auxHeatMap = []
          response.extended_hierarchy[0].map((item)=>{
            auxDendogram.push(item.slice(0,5))
            auxHeatMap.push(item.slice(1,5))
          })
          setDendogramData(auxDendogram)
          setHeatMapData(auxHeatMap)
        }
        setDiseaseData()
      },[])

    return(
        <>
            <CustomAppBar/>
            <Sidebar>
                <Dendogram data={dendogramData} />
                <Box sx={{display: 'flex'}}>
                    <TreeMap data={heatMapData} />
                    <InfoCard />
                </Box>
            </Sidebar>
        </>
    )
}