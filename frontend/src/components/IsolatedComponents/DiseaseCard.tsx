import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Typography from '@mui/material/Typography';
import CardActionArea from '@mui/material/CardActionArea';
import { CardActions, Chip } from '@mui/material';
import NoImageAvailable from '../../assets/no-image.png'
import { useNavigate } from 'react-router-dom';

interface Props {
    diseaseTitle: string;
    description: string
    phenotypes: [Filter];
    anatomy: [Filter];
    ageOnSet: [Filter];
    media?: string,
    id: string
}

interface Filter{
    label: string
}

function getIdFromUrl(url: string){
    const auxString = url.split('/')
    return auxString[auxString.length -1]
}



export default function DiseaseCard({diseaseTitle, phenotypes,description, media, anatomy, ageOnSet, id}: Props){

    const navigate = useNavigate();

    return(
        
            <Card sx={{ width: 345, height: 300, color: '#1d8bf8', border: 1, marginTop: 2 }}>
                <CardActionArea onClick={()=>navigate('/main/' + getIdFromUrl(id))}>
                <CardMedia
                    component="img"
                    height="140"
                    image={media ? media : NoImageAvailable}
                    alt={"No image available"}
                />
                <CardContent>
                    <Typography sx={{textDecoration:'none'}} gutterBottom variant={diseaseTitle.length > 22 ? "h6" :"h5"} component="div" >
                        {diseaseTitle}
                    </Typography>
                    <Typography variant="body2" paragraph noWrap sx={{ color: 'text.secondary' }}>
                        {description}
                    </Typography>
                </CardContent>
                </CardActionArea>
                <CardActions sx={{display: 'flex', justifyContent: 'flex-end'}}>
                    {
                        phenotypes.slice(0,2).map((item)=>(
                            <Chip label={item.label} color="secondary" size='small' />
                        ))
                    }
                    {
                        anatomy.slice(0,2).map((item)=>(
                            <Chip label={item.label} color="error" size='small' />
                        ))
                    }
                    {
                        ageOnSet.slice(0,1).map((item)=>(
                            <Chip label={item.label} color='primary' size='small' />
                        ))
                    }
                </CardActions>
            </Card>
         )
}