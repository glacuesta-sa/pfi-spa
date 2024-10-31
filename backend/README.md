# Repositorio Backend
Repositorio que contiene:
- Contenedor para la generación de modelo de datos y entrenamiento de modelos. (Pipeline ETL)
- Contenedor para la API backend con endpoints para integración con frontend.

## Requisitos
- Docker / Docker Compose - Descargar e instalar Docker o Docker Desktop.

## Dependencias
- MongoDB -> Persistencia de modelo de datos y fallback en caso de no proveer credenciales de AWS y S3.
- Flask -> Framework para la API REST y servicios de exploración visual y predicciones

## Ejecutar
docker compose up --build web

Levanta en:
http://127.0.0.1:80

# API REST
Acceder a toda la especificación de la API REST: \
http://127.0.0.1:80/v1/docs 

Tambien está accesible a través del siguiente link público: \
https://app.swaggerhub.com/apis/GAXELAC_1/apollod-pfi-spa-lacuesta-rondan/1.0.0#/

Ejemplo para obtener la enfermedad "inflammatory disease" \
http://127.0.0.1:80/v1/disease/MONDO_0021166

# MONGO DB
Connection String (default): mongodb://localhost:27018/

Se puede utilizar Mongo DB Compass para acceder.

## Modelo de Datos
```mermaid
classDiagram
    class Disease {
        +String id
        +String name
        +String description
        +String titulo
        +String parentDisease
        +List childrenDiseases
        +List causes
        +List treatments
        +List anatomical_structures
        +List phenotypes
        +List exposures
        +List chemicals
        +List age_onsets
    }

    class Chemical {
        +String id
        +String name
        +String description
    }

    class Exposure {
        +String id
        +String name
        +String description
    }

    class Phenotype {
        +String id
        +String name
        +String description
    }

    class Relationship {
        +String id
        +String name
        +String description
    }

    class Treatment {
        +String id
        +String name
        +String description
    }

    class Anatomical {
        +String id
        +String name
        +String description
    }

    Disease --> "1" Disease : parentDisease
    Disease --> "0..*" Disease : childrenDiseases
    Disease --> "1..*" Relationship : tiene
    Disease --> "1..*" Chemical : tiene
    Disease --> "1..*" Exposure : tiene
    Disease --> "1..*" Phenotype : tiene
    Disease --> "1..*" Treatment : tiene
    Disease --> "1..*" Anatomical : tiene
