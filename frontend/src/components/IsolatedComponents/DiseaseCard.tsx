import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Typography from '@mui/material/Typography';
import CardActionArea from '@mui/material/CardActionArea';
import { CardActions, Chip } from '@mui/material';
import { Description } from '@mui/icons-material';

interface Props {
    diseaseTitle: string;
    description: string
    phenotypes: [Phenotype]
}

interface Phenotype{
    label: string
}

export default function DiseaseCard({diseaseTitle, phenotypes,description}: Props){
    console.log('Pheno',phenotypes)
    return(
        <Card sx={{ maxWidth: 345, maxHeight: 600, color: '#1d8bf8', border: 1 }}>
            <CardActionArea>
            <CardMedia
                component="img"
                height="140"
                image="/static/images/cards/contemplative-reptile.jpg"
                alt="green iguana"
            />
            <CardContent>
                <Typography gutterBottom variant={diseaseTitle.length > 22 ? "h6" :"h5"} component="div" >
                    {diseaseTitle}
                </Typography>
                <Typography variant="body2" paragraph noWrap sx={{ color: 'text.secondary' }}>
                    {description}
                </Typography>
            </CardContent>
            </CardActionArea>
            <CardActions sx={{display: 'flex', justifyContent: 'flex-end'}}>
                {
                    phenotypes.map((phenotype)=>(
                        <Chip label={phenotype.label} color='primary' />
                    ))
                }
            </CardActions>
         </Card>)
}