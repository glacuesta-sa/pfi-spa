import { Checkbox, List, ListItem, ListItemButton, ListItemIcon, ListItemText } from "@mui/material";
import React, { Dispatch, SetStateAction } from "react";
import { getRelationshipTypesFilter } from "../../services/webService";

interface Item {
  value?: string,
  label?: string
}

interface Props {
  setSelection: Dispatch<SetStateAction<Item>>
}

export default function RelationshipTypeFilter({setSelection}: Props){
    const [options, setOptions] = React.useState<Array<Item>>([])
    const [selected, setSelected] = React.useState<string>()
  
    const handleToggle = (item: Item) => () => {
      if(item.label === selected){
        setSelected(undefined)
        setSelection({label: undefined, value: undefined})
      }else{
        setSelection(item)  
        setSelected(item.label)
      }
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
                    checked={(item.label) === selected}
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