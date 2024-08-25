
import Chip from '@mui/material/Chip';

interface Props {
  text: string,
  removeFunction: (value: string)=>void
}


export default function CustomChip({text, removeFunction} : Props) {
  const handleClick = () => {
    console.info('You clicked the Chip.');
  };

  const handleDelete = () => {
    console.info('You clicked the Chip.');
    removeFunction(text)
  };

  return (
      <Chip
        color='primary'
        label={text}
        onClick={handleClick}
        onDelete={handleDelete}
        sx={{margin: 0.25}}
      />
  );
}