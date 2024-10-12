# APOLLOD
![image](./static/apollod.png)
Prototipo para predicción y exploración visual de términos médicos utilizando fuentes Linked Open Data (LOD).

## ¿Qué es APOLLOD?
APOLLOD es el resultado obtenido de un proyecto final de ingeniería realizado en el año 2024, que busca eliminar la curva de aprendizaje de las tecnologías subyacentes a LOD utilizando técnicas de exploración visual y aprendizaje automático. 

Este prototipo permite el diagnóstico de enfermedes a través de la sintomatología, que es la utilización de signos o síntomas visibles de una enfermedad para realizar un diagnósitico presuntivo. Todo esto utilizando fuentes de datos LOD, como son las ontologías de MONDO, HPO, UBERON, etc.

Este esta enmarcado en el proyecto de investigación “P24T02 – Tecnologías de la Información facilitadoras para Linked Open Data (LOD)” del Instituto de Tecnología (INTEC) de la Universidad Argentina de la Empresa (UADE).

### ¿Por qué APOLLOD?
Apolo: el dios griego de la medicina y el conocimiento. \
LOD: Linked Open Data o Datos Abiertos Enlazados, el corazón del prototipo, su fuente de datos.

# Ejecutar el el proyecto
Revisa el siguiente contenido para ejecutar el proyecto localmente.

## Backend
Para más información sobre el backend: \
./backend/README.md

### Ejecutar backend
1. docker compose -f ./backend/docker-compose.yaml up --build

Levanta en:
http://127.0.0.1:5000

## Frontend
Para más información sobre el frontend: \
./frontend/README.md

### Ejecutar Frontend
1. cd ./frontend
2. npm run dev

Levanta en:
http://127.0.0.1:5173/

# Descarga de Responsabilidad
El prototipo se desarrolla con la intención de generar conocimiento replicable en el área y únicamente con fines informativos y educativos. La información proporcionada no debe ser utilizada como sustituto de la consulta médica profesional.
Debido a que las fuentes de datos son de orígenes externos este proyecto no garantiza la exactitud o integridad de la información proporcionada, pese a que las fuentes aplican procesos pertinentes para la curación y validación de los datos. El uso de esta aplicación no crea una relación médico-paciente y no debería retrasar la búsqueda de consejo médico profesional.

# Referencias
Este proyecto utiliza [MONDO](https://github.com/monarch-initiative/mondo) como fuente de datos principal.

