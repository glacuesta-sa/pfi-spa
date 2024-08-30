import * as React from 'react';
import TextField from '@mui/material/TextField';
import Autocomplete from '@mui/material/Autocomplete';
import { getPhenotypes } from '../../services/webService';

export default function SymptomsFilter({updateSymptom, updateFilterArray}:{updateSymptom:(value: string)=>void, updateFilterArray:(value: string)=>void}) {
  const [value, setValue] = React.useState<string | null>();
  const [inputValue, setInputValue] = React.useState('');
  const [optionsLabel, setOptionsLabel] = React.useState([])
  const [options, setOptions] = React.useState([])

  React.useEffect(()=>{
    async function setPhenotypes(){
      const filters = await getPhenotypes()
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
        // @ts-ignore
        onChange={(event: any, newValue: string | null) => {
          setValue(newValue);
          if(newValue){
            updateSymptom(newValue)
            const aux = options.find((item)=> item.label === newValue)
            updateFilterArray(aux.value)
          }
        }}
        // @ts-ignore
        onInputChange={(event, newInputValue) => {
          setInputValue(newInputValue);
        }}
        inputValue={inputValue}
        id="controllable-states-demo"
        options={optionsLabel}
        sx={{ width: 300 }}
        renderInput={(params) => <TextField {...params} label="Seleccione los Sintomas" />}
      />
  );
}