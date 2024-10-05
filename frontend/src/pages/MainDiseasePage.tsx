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
    const [loadingTrigger, setLoadingTrigger] = useState<boolean>(false)

    const [dendogramData, setDendogramData] = useState()
    const [heatMapData, setHeatMapData] = useState()

    // @ts-expect-error unable to type array of arrays
    function getTreeDataItem(item, data){
      
      if(item[0] !== 'id'){
        const disease = item[1]
        // @ts-expect-error unable to type array of arrays
        const auxParent = item[2] === -1 ? [null,null] : data.find((e)=>e[0]===item[2])
        const size = item[3]
        // const color = item[4]
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
          // @ts-expect-error no logical empty value
          const response = await getChartsData(diseaseId)
          // @ts-expect-error unable to type array of arrays
          const auxDendogram = []
          // @ts-expect-error unable to type array of arrays
          const auxHeatMap = []
          // @ts-expect-error unable to type array of arrays
          response.extended_hierarchy[0].map((item)=>{
            const auxItem = getTreeDataItem(item, response.extended_hierarchy[0])
            auxDendogram.push(item.slice(0,5))
            auxHeatMap.push(auxItem)
          })
          // @ts-expect-error unable to type array of arrays
          setDendogramData(auxDendogram)
          // @ts-expect-error unable to type array of arrays
          setHeatMapData(auxHeatMap)
        }
        setDiseaseData()
      },[diseaseId, loadingTrigger])

    return(
        <>
            <CustomAppBar/>
            <SidebarDisease setLoadingTrigger={setLoadingTrigger} diseaseId={diseaseId ? diseaseId :'' }>
                <Dendogram data={dendogramData} loadingUpdate={loadingTrigger}/>
                <Box sx={{display: 'flex'}}>
                    <TreeMap data={heatMapData} />
                    <InfoCard />
                </Box>
            </SidebarDisease>
        </>
    )
}