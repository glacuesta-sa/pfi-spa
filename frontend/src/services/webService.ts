const url = 'http://127.0.0.1:5000'

export async function getPhenotypes(): Promise<any>{
    try {
        const response = await fetch(`${url}/phenotypes`,{
            method: 'GET',
            mode: "cors",
            headers:{   
                'Accept':'*/*'
            }
        })
        return await response.json()

    } catch (error){
        console.log("error", error)
        return []
    }
}

export async function getAnatomicalStructures(){
    try {
        const response = await fetch(`${url}/anatomical_structures`,{
            method: 'GET',
            mode: "cors",
            headers:{   
                'Accept':'*/*'
            }
        })
        return await response.json()

    } catch (error){
        console.log("error", error)
        return []
    }
}

export async function getAgesFilter(){
    try {
        const response = await fetch(`${url}/age_onsets`,{
            method: 'GET',
            mode: "cors",
            headers:{   
                'Accept':'*/*'
            }
        })
        return await response.json()

    } catch (error){
        console.log("error", error)
        return []
    }
}

export async function getRelationshipTypesFilter(){
    try {
        // const response = await fetch(`${url}/age_onsets`,{
        //     method: 'GET',
        //     mode: "cors",
        //     headers:{   
        //         'Accept':'*/*'
        //     }
        // })
        // return await response.json()
        return[{label:'Relationship 1', value: '1'}, {label:'Relationship 2', value: '2'}]
    } catch (error){
        console.log("error", error)
        return []
    }
}

export async function getChartsData(diseaseId: string) {
    try {
        const response = await fetch(`${url}/diseases/${diseaseId}/hierarchy`,{
            method: 'GET',
            mode: "cors",
            headers:{   
                'Accept':'*/*'
            }
        })
        return await response.json()
    } catch (error){
        console.log("error", error)
        return []
    }
}

export async function getDiseaseById(diseaseId: string) {
    try {
        const response = await fetch(`${url}/diseases/${diseaseId}`,{
            method: 'GET',
            mode: "cors",
            headers:{   
                'Accept':'*/*'
            }
        })
        return await response.json()
    } catch (error){
        console.log("error", error)
        return []
    }
}

export async function getDiseasesByFilters(phenotype_ids: Array<string>, anatomical_ids: Array<string>, age_onset_ids: Array<string>) {
    try {
        const response = await fetch(`${url}/diseases/filter`, {
            method: 'POST',
            mode: "cors",
            headers:{   
                'Accept':'*/*',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                phenotype_ids: phenotype_ids,
                anatomical_ids: anatomical_ids,
                age_onset_ids: age_onset_ids,
                chemical_ids:[],
                treatment_ids:[],
                exposure_ids:[]
            })
        })
        return await response.json()

    } catch (error){
        console.log("error", error)
        return []
    }
}
