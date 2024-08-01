
import Chip from '@mui/material/Chip';

export default function CustomChip({text}:{text: string}) {
  const handleClick = () => {
    console.info('You clicked the Chip.');
  };

  const handleDelete = () => {
    console.info('You clicked the delete icon.');
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