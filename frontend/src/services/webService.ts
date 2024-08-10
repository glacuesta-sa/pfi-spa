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
    }
}

export async function getChartsData(diseaseId: string) {
    try {
        const response = await fetch(`${url}/filter_hierarchy/${diseaseId}`,{
            method: 'GET',
            mode: "cors",
            headers:{   
                'Accept':'*/*'
            }
        })
        return await response.json()
    } catch (error){
        console.log("error", error)
    }
}

export async function getDiseaseById(diseaseId: string) {
    try {
        const response = await fetch(`${url}/disease/${diseaseId}`,{
            method: 'GET',
            mode: "cors",
            headers:{   
                'Accept':'*/*'
            }
        })
        return await response.json()
    } catch (error){
        console.log("error", error)
    }
}

export async function getDiseasesByFilters(phenotype_ids: Array<string>, anatomical_ids: Array<string>, age_onset_ids: Array<string>) {
    try {
        console.log(`ENTERING NEW `)
        const response = await fetch(`${url}/diseases/by_filters`, {
            method: 'POST',
            mode: "cors",
            headers:{   
                'Accept':'*/*',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                phenotype_ids: phenotype_ids,
                anatomical_ids: anatomical_ids,
                age_onset_ids: age_onset_ids
            })
        })
        return await response.json()

    } catch (error){
        console.log("error", error)
    }
}
