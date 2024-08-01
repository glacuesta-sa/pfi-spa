import * as React from 'react';
import TextField from '@mui/material/TextField';
import Autocomplete from '@mui/material/Autocomplete';

const options = ['Dolor abdominal', 'Nivel bajo de sodio','Tos', 'Entumecimiento', 'Lengua amarilla', 'Vomitos', 'Dolor de cabeza', 'Fiebre','Insomnio','Convulsiones'];

export default function SymptomsFilter({updateSymptom}:{updateSymptom:(value: string)=>void}) {
  const [value, setValue] = React.useState<string | null>();
  const [inputValue, setInputValue] = React.useState('');

  return (
      <Autocomplete
        value={value}
        // @ts-ignore
        onChange={(event: any, newValue: string | null) => {
          setValue(newValue);
          if(newValue){
            updateSymptom(newValue)
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
        renderInput={(params) => <TextField {...params} label="Seleccione los Sintomas" />}
      />
  );
}