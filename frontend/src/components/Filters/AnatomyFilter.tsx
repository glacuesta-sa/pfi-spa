import * as React from 'react';
import TextField from '@mui/material/TextField';
import Autocomplete from '@mui/material/Autocomplete';

const options = ['Cerebro','Corazon','Pulmones','Riñones','Lobulo Frontal','Dermis','Laringe'];

export default function AnatomyFilter({updateSelection}:{updateSelection:(value: string)=>void}) {
  const [value, setValue] = React.useState<string | null>();
  const [inputValue, setInputValue] = React.useState('');

  return (
      <Autocomplete
        value={value}
        onChange={(event: any, newValue: string | null) => {
          setValue(newValue);
          if(newValue){
            updateSelection(newValue)
          }
        }}
        onInputChange={(event, newInputValue) => {
          setInputValue(newInputValue);
        }}
        inputValue={inputValue}
        // onInputChange={(event, newInputValue) => {
        //   updateSelection(newInputValue);
        // }}
        id="controllable-states-demo"
        options={options}
        sx={{ width: 300 }}
        renderInput={(params) => <TextField {...params} label="Anatomia Involucrada" />}
      />
  );
}