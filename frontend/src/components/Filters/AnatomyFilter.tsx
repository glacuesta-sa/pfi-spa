import * as React from 'react';
import TextField from '@mui/material/TextField';
import Autocomplete from '@mui/material/Autocomplete';
import { getAnatomicalStructures } from '../../services/webService';


interface Item {
  value: string,
  label: string
}

export default function AnatomyFilter({updateSelection, updateAnatomicFilterArray}:{updateSelection:(value: string)=>void, updateAnatomicFilterArray:(value: string)=>void}) {
  const [value, setValue] = React.useState<string | null>();
  const [inputValue, setInputValue] = React.useState('');
  const [optionsLabel, setOptionsLabel] = React.useState<string[]>([])
  const [options, setOptions] = React.useState<Item[]>([])

  React.useEffect(()=>{
    async function setAnatomy(){
      const filters: Item[] = await getAnatomicalStructures()
      const aux = filters.map((item)=> item.label)
      const aux2 = filters.map((item)=> item)
      setOptionsLabel(aux)
      setOptions(aux2)
    }
    setAnatomy()
  },[])

  return (
      <Autocomplete
        value={value}
        // @ts-expect-error event is needed but not used
        onChange={(event: React.FormEvent<HTMLInputElement>, newValue: string | null) => {
          setValue(newValue);
          if(newValue){
            updateSelection(newValue)
            const aux = options.find((item)=> item.label === newValue)
            // @ts-expect-error no logical empty value
            updateAnatomicFilterArray(aux.value)
          }
        }}
        // @ts-expect-error Event is needed but not used
        onInputChange={(event, newInputValue) => {
          setInputValue(newInputValue);
        }}
        inputValue={inputValue}
        id="controllable-states-demo"
        options={optionsLabel}
        sx={{ width: 300 }}
        renderInput={(params) => <TextField {...params} label="Anatomy Involved" />}
      />
  );
}