from flask import jsonify, request, abort
from bson import ObjectId
from db import diseases_collection
from models import get_data_model
import utils

def init_routes(app):

    @app.route("/diseases", methods=["GET"])
    def get_diseases():
        diseases = list(diseases_collection.find({}, {'_id': 0}))
        return jsonify(diseases)

    @app.route("/disease/<mondo_id>", methods=["GET"])
    def get_disease(mondo_id):
        full_id = f"http://purl.obolibrary.org/obo/{mondo_id}"
        disease = diseases_collection.find_one({"id": full_id}, {'_id': 0})
        if disease:
            return jsonify(disease)
        else:
            abort(404, description="Disease not found")

    @app.route("/hierarchy", methods=["GET"])
    def get_hierarchy():
        hierarchy = utils.build_parent_child_hierarchy()
        return jsonify(hierarchy)

    @app.route("/filter_hierarchy/<mondo_id>", methods=["GET"])
    def filter_hierarchy(mondo_id):
        full_id = f"http://purl.obolibrary.org/obo/{mondo_id}"
        if not diseases_collection.find_one({"id": full_id}):
            abort(404, description="Disease not found")
        hierarchy = utils.filter_hierarchy_by_mondo_id(full_id)
        return jsonify(hierarchy)
    
    @app.route("/diseases/by_phenotypes", methods=["POST"])
    def diseases_by_phenotypes():
        phenotype_ids = request.json.get('phenotype_ids')
        if not phenotype_ids:
            abort(400, description="Phenotype IDs are required")
        
        print(f"Received phenotype IDs: {phenotype_ids}")
        # Transform the phenotype IDs to include the full URI
        full_phenotype_ids = [f"http://purl.obolibrary.org/obo/{pid}" for pid in phenotype_ids]
        print(f"Transformed phenotype IDs: {full_phenotype_ids}")

        diseases = utils.get_diseases_by_phenotypes(full_phenotype_ids, get_data_model())
        diseases = utils.convert_objectid_to_str(diseases)
        print(f"Found diseases: {diseases}")
        return jsonify(diseases)
    
    @app.route("/diseases/by_age_onsets", methods=["POST"])
    def diseases_by_age_onsets():
        age_onset_ids = request.json.get('age_onset_ids')
        if not age_onset_ids:
            abort(400, description="Age onset IDs are required")
        
        print(f"Received age onset IDs: {age_onset_ids}")
        # Transform the age onset IDs to include the full URI
        full_age_onset_ids = [f"http://purl.obolibrary.org/obo/{aid}" for aid in age_onset_ids]
        print(f"Transformed age onset IDs: {full_age_onset_ids}")

        diseases = utils.get_diseases_by_age_onsets(full_age_onset_ids, get_data_model())
        diseases = utils.convert_objectid_to_str(diseases)
        print(f"Found diseases: {diseases}")
        return jsonify(diseases)

    @app.route("/diseases/by_anatomical_structures", methods=["POST"])
    def diseases_by_anatomical_structures():
        anatomical_ids = request.json.get('anatomical_ids')
        if not anatomical_ids:
            abort(400, description="Anatomical structure IDs are required")
        
        print(f"Received anatomical structure IDs: {anatomical_ids}")
        # Transform the anatomical structure IDs to include the full URI
        full_anatomical_ids = [f"http://purl.obolibrary.org/obo/{aid}" for aid in anatomical_ids]
        print(f"Transformed anatomical structure IDs: {full_anatomical_ids}")

        diseases = utils.get_diseases_by_anatomical_structures(full_anatomical_ids, get_data_model())
        diseases = utils.convert_objectid_to_str(diseases)
        print(f"Found diseases: {diseases}")
        return jsonify(diseases)
    
    @app.route("/diseases/by_filters", methods=["POST"])
    def diseases_by_filters():
        filters = request.json
        phenotype_ids = filters.get('phenotype_ids', [])
        anatomical_ids = filters.get('anatomical_ids', [])
        age_onset_ids = filters.get('age_onset_ids', [])
        
        # Transform the IDs to include the full URI
        full_phenotype_ids = [f"http://purl.obolibrary.org/obo/{pid}" for pid in phenotype_ids]
        full_anatomical_ids = [f"http://purl.obolibrary.org/obo/{aid}" for aid in anatomical_ids]
        full_age_onset_ids = [f"http://purl.obolibrary.org/obo/{aid}" for aid in age_onset_ids]

        diseases = utils.get_diseases_by_filters(full_phenotype_ids, full_anatomical_ids, full_age_onset_ids, get_data_model())
        diseases = utils.convert_objectid_to_str(diseases)
        return jsonify(diseases)

    @app.route("/phenotypes", methods=["GET"])
    def get_phenotypes():
        phenotypes = []
        for disease in get_data_model()['diseases']:
            for phenotype in disease.get('phenotypes', []):
                phenotypes.append({
                    "label": phenotype.get('label', 'Unknown Phenotype'),
                    "value": phenotype['target'].replace("http://purl.obolibrary.org/obo/", "")
                })
        
        # Remove duplicates
        unique_phenotypes = {v['value']: v for v in phenotypes}.values()
        return jsonify(list(unique_phenotypes))

    @app.route("/anatomical_structures", methods=["GET"])
    def get_anatomical_structures():
        anatomical_structures = []
        for disease in get_data_model()['diseases']:
            for anatomical_structure in disease.get('anatomical_structures', []):
                anatomical_structures.append({
                    "label": anatomical_structure.get('label', 'Unknown anatomical structure'),
                    "value": anatomical_structure['target'].replace("http://purl.obolibrary.org/obo/", "")
                })
        
        # Remove duplicates
        unique_anatomical_structures = {v['value']: v for v in anatomical_structures}.values()
        return jsonify(list(unique_anatomical_structures))

    @app.route("/age_onsets", methods=["GET"])
    def get_age_onsets():
        age_onsets = []
        for disease in get_data_model()['diseases']:
            for age_onset in disease.get('age_onsets', []):
                age_onsets.append({
                    "label": age_onset.get('label', 'Unknown age onset'),
                    "value": age_onset['target'].replace("http://purl.obolibrary.org/obo/", "")
                })
        
        # Remove duplicates
        unique_age_onsets = {v['value']: v for v in age_onsets}.values()
        return jsonify(list(unique_age_onsets))
