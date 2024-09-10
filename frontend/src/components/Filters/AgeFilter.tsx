import * as React from 'react';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Checkbox from '@mui/material/Checkbox';
import { getAgesFilter } from '../../services/webService';

interface Item {
  value: string,
  label: string
}

interface Props {
  updateAgeFilterArray: (value: string, remove?: boolean)=>void
}

export default function AgeFilter({updateAgeFilterArray}: Props) {
  const [checked, setChecked] = React.useState<Array<string>>([]);
  const [options, setOptions] = React.useState<Array<Item>>([])

  const handleToggle = (item: {value: string, label:string}) => () => {
    const currentIndex = checked.indexOf(item.label);
    const newChecked = [...checked];

    if (currentIndex === -1) {
      newChecked.push(item.label);
      updateAgeFilterArray(item.value, false)
    } else {
      newChecked.splice(currentIndex, 1);
      updateAgeFilterArray(item.value, true)
    }
    setChecked(newChecked);
  };

  React.useEffect(()=>{
    async function setAgeFilter(){
      const response = await getAgesFilter()
      setOptions(response)
    }
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
            <ListItemButton role={undefined} onClick={handleToggle(item)} dense>
              <ListItemIcon>
                <Checkbox
                  edge="start"
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