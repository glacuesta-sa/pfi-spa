import { Checkbox, List, ListItem, ListItemButton, ListItemIcon, ListItemText } from "@mui/material";
import React from "react";
import { getRelationshipTypesFilter } from "../../services/webService";

interface Item {
    value: string,
    label: string
  }

export default function RelationshipTypeFilter(){
    const [checked, setChecked] = React.useState<Array<string>>([]);
    const [options, setOptions] = React.useState<Array<Item>>([])
  
    const handleToggle = (item: {value: string, label:string}) => () => {
      const currentIndex = checked.indexOf(item.label);
      const newChecked = [...checked];
  
      if (currentIndex === -1) {
        newChecked.push(item.label);
      } else {
        newChecked.splice(currentIndex, 1);
      }
      setChecked(newChecked);
    };
  

      React.useEffect(()=>{
        async function setAgeFilter(){
          const response = await getRelationshipTypesFilter()
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
              key={item.label}
              disablePadding
            >
              <ListItemButton role={undefined} onClick={handleToggle(item)} dense>
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