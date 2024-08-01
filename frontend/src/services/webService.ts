const url = 'http://127.0.0.1:5000'

export async function getPhenotypes(): Promise<any>{
    try {
        let response = await fetch(`${url}/phenotypes`,{
            method: 'GET',
            mode: "cors",
            headers:{   
                'Accept':'*/*',
                'Host':'http://localhost:5173'
            }
        })
        return await response.json()

    } catch (error){
        console.log("error", error)
    }
}

export async function getAnatomicalStructures(){
    try {
        let response = await fetch(`${url}/anatomical_structures`,{
            method: 'GET',
            mode: "cors",
            headers:{   
                'Accept':'*/*',
                'Host':'http://localhost:5173'
            }
        })
        return await response.json()

    } catch (error){
        console.log("error", error)
    }
}

export async function getChartsData(diseaseId: string) {
    try {
        let response = await fetch(`${url}/filter_hierarchy/${diseaseId}`,{
            method: 'GET',
            mode: "cors",
            headers:{   
                'Accept':'*/*',
                'Host':'http://localhost:5173'
            }
        })
        
        return await response.json()

    } catch (error){
        console.log("error", error)
    }
}
