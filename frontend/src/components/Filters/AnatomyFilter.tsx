import * as React from 'react';
import TextField from '@mui/material/TextField';
import Autocomplete from '@mui/material/Autocomplete';
import { getAnatomicalStructures } from '../../services/webService';


export default function AnatomyFilter({updateSelection}:{updateSelection:(value: string)=>void}) {
  const [value, setValue] = React.useState<string | null>();
  const [inputValue, setInputValue] = React.useState('');
  const [options, setOptions] = React.useState([])

  React.useEffect(()=>{
    async function setAnatomy(){
      const filters = await getAnatomicalStructures()
      const aux = filters.map((item)=> item.label)
      setOptions(aux)
    }
    setAnatomy()
  },[])

  return (
      <Autocomplete
        value={value}
        // @ts-ignore
        onChange={(event: any, newValue: string | null) => {
          setValue(newValue);
          if(newValue){
            updateSelection(newValue)
          }
        }}
        // @ts-ignore
        onInputChange={(event, newInputValue) => {
          setInputValue(newInputValue);
        }}
        inputValue={inputValue}
        id="controllable-states-demo"
        options={options}
        sx={{ width: 300 }}
        renderInput={(params) => <TextField {...params} label="Anatomia Involucrada" />}
      />
  );
}