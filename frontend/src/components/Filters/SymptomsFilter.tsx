import * as React from 'react';
import TextField from '@mui/material/TextField';
import Autocomplete from '@mui/material/Autocomplete';
import { getPhenotypes } from '../../services/webService';


interface Item {
  value: string,
  label: string
}

export default function SymptomsFilter({updateSymptom, updateFilterArray}:{updateSymptom:(value: string)=>void, updateFilterArray:(value: string)=>void}) {
  const [value, setValue] = React.useState<string | null>();
  const [inputValue, setInputValue] = React.useState('');
  const [optionsLabel, setOptionsLabel] = React.useState<string[]>([])
  const [options, setOptions] = React.useState<Item[]>([])

  React.useEffect(()=>{
    async function setPhenotypes(){
      const filters: Item[] = await getPhenotypes()
      const aux = filters.map((item)=> item.label)
      const aux2 = filters.map((item)=> item)
      setOptionsLabel(aux)
      setOptions(aux2)
    }
    setPhenotypes()
  },[])

  return (
      <Autocomplete
        value={value}
        // @ts-expect-error Event is needed
        onChange={(event: React.FormEvent<HTMLInputElement>, newValue: string | null) => {
          setValue(newValue);
          if(newValue){
            updateSymptom(newValue)
            const aux = options.find((item)=> item.label === newValue)
            // @ts-expect-error no logical empty value
            updateFilterArray(aux.value)
          }
        }}
        // @ts-expect-error Event is needed
        onInputChange={(event, newInputValue) => {
          setInputValue(newInputValue);
        }}
        inputValue={inputValue}
        id="controllable-states-demo"
        options={optionsLabel}
        sx={{ width: 300 }}
        renderInput={(params) => <TextField {...params} label="Select Symptoms" />}
      />
  );
}