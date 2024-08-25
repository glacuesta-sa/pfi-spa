import { Box } from "@mui/material";
import Dendogram from "../components/Charts/Dendogram";
import CustomAppBar from "../components/Layout/Appbar";
import SidebarDisease from "../components/Layout/SidebarDisease";
import TreeMap from "../components/Charts/TreeMap";
import InfoCard from "../components/Charts/InfoCard";
import { useState, useEffect } from "react";
import { getChartsData } from "../services/webService";
import { useParams } from "react-router-dom";



export default function MainDiseasePage(){

    const {diseaseId} = useParams()

    const [dendogramData, setDendogramData] = useState()
    const [heatMapData, setHeatMapData] = useState()

    function getTreeDataItem(item, data){
      
      if(item[0] !== 'id'){
        const disease = item[1]
        const auxParent = item[2] === -1 ? [null,null] : data.find((e)=>e[0]===item[2])
        const size = item[3]
        const color = item[4]
        return [disease, auxParent[1], size, size]
      }else{
        return [
              "Disease",
              "Parent",
              "size",
              "color",
            ]
      }
    }

    useEffect(()=>{
        async function setDiseaseData(){
          const response = await getChartsData(diseaseId)
          const auxDendogram = []
          const auxHeatMap = []
          response.extended_hierarchy[0].map((item, index)=>{
            const auxItem = getTreeDataItem(item, response.extended_hierarchy[0])
            auxDendogram.push(item.slice(0,5))
            auxHeatMap.push(auxItem)
          })
          setDendogramData(auxDendogram)
          setHeatMapData(auxHeatMap)
        }
        setDiseaseData()
      },[])

    return(
        <>
            <CustomAppBar/>
            <SidebarDisease>
                <Dendogram data={dendogramData} />
                <Box sx={{display: 'flex'}}>
                    <TreeMap data={heatMapData} />
                    <InfoCard />
                </Box>
            </SidebarDisease>
        </>
    )
}