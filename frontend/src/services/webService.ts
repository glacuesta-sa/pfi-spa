const url = 'http://127.0.0.1:80/v1'

export async function getPhenotypes(){
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
        const response = await fetch(`${url}/relationship_types`,{
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
        const aux = await response.json()
        if(aux.error){
            return []
        }
        return aux

    } catch (error){
        console.log("error", error)
        return []
    }
}

export async function postPrediction(disease_id: string, new_relationship_property: string | undefined) {
    try {
        const response = await fetch(`${url}/diseases/predict`, {
            method: 'POST',
            mode: "cors",
            headers:{   
                'Accept':'*/*',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                disease_id: disease_id,
                new_relationship_property: new_relationship_property
            })
        })
        const aux = await response.json()
        return aux

    } catch (error){
        console.log("error", error)
        return []
    }
}


