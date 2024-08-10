import * as React from 'react';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Checkbox from '@mui/material/Checkbox';
import { getAgesFilter } from '../../services/webService';


export default function AgeFilter() {
  const [checked, setChecked] = React.useState([0]);
  const [options, setOptions] = React.useState([])

  const handleToggle = (value: number) => () => {
    const currentIndex = checked.indexOf(value);
    const newChecked = [...checked];

    if (currentIndex === -1) {
      newChecked.push(value);
    } else {
      newChecked.splice(currentIndex, 1);
    }

    setChecked(newChecked);
  };

  React.useEffect(()=>{
    async function setAgeFilter(){
      const response = await getAgesFilter()
      setOptions(response)
    }
    console.log(`Age filters!`)
    setAgeFilter()
  }, [])

  return (
    <List sx={{ width: '100%', maxWidth: 360, bgcolor: 'background.paper' }}>
      {options.map((item) => {
        const labelId = `checkbox-list-label-${item.label}`;

        return (
          <ListItem
            key={item.value}
            disablePadding
          >
            <ListItemButton role={undefined} onClick={handleToggle(parseInt(item.label))} dense>
              <ListItemIcon>
                <Checkbox
                  edge="start"
                  // @ts-ignore
                  checked={checked.indexOf(item.label) !== -1}
                  tabIndex={-1}
                  disableRipple
                  inputProps={{ 'aria-labelledby': labelId }}
                />
              </ListItemIcon>
              <ListItemText id={labelId} primary={item.label} primaryTypographyProps={{fontSize: 16}}/>
            </ListItemButton>
          </ListItem>
        );
      })}
    </List>
  );
}