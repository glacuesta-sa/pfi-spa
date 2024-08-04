from flask import jsonify, request
import db
import utils

def init_routes(app):

    @app.route("/diseases", methods=["GET"])
    def get_diseases():
        diseases = list(db.get_diseases_collection())
        return utils.create_json_response(jsonify(diseases), 200)

    @app.route("/disease/<mondo_id>", methods=["GET"])
    def get_disease(mondo_id):
        full_id = f"http://purl.obolibrary.org/obo/{mondo_id}"
        disease = db.get_disease_by_id(full_id)
        if disease:
            try:
               utils.set_llm_fields(disease)
            except Exception as e:
                return utils.create_json_response(jsonify({"error": str(e)}), 500)

            return utils.create_json_response(jsonify(disease), 200)
        else:
            return utils.create_json_response(jsonify("Disease not found"), 404)

    @app.route("/hierarchy", methods=["GET"])
    def get_hierarchy():
        hierarchy = utils.build_parent_child_hierarchy()
        return utils.create_json_response(jsonify(hierarchy), 200)

    @app.route("/filter_hierarchy/<mondo_id>", methods=["GET"])
    def filter_hierarchy(mondo_id):
        full_id = f"http://purl.obolibrary.org/obo/{mondo_id}"
        if not db.get_disease_by_id(full_id):
            return utils.create_json_response(jsonify("Disease not found"), 404)
        hierarchy = utils.filter_hierarchy_by_mondo_id(full_id)
        return utils.create_json_response(jsonify(hierarchy), 200)
    
    @app.route("/diseases/by_phenotypes", methods=["POST"])
    def diseases_by_phenotypes():
        phenotype_ids = request.json.get('phenotype_ids')
        if not phenotype_ids:
           return utils.create_json_response(jsonify("Phenotype IDs are required"), 400)
        
        print(f"Received phenotype IDs: {phenotype_ids}")
        # Transform the phenotype IDs to include the full URI
        full_phenotype_ids = [f"http://purl.obolibrary.org/obo/{pid}" for pid in phenotype_ids]
        print(f"Transformed phenotype IDs: {full_phenotype_ids}")

        diseases = utils.get_diseases_by_phenotypes(full_phenotype_ids, db.get_data_model())
        diseases = utils.convert_objectid_to_str(diseases)
        print(f"Found diseases: {diseases}")
        return utils.create_json_response(jsonify(diseases), 200)
    
    @app.route("/diseases/by_age_onsets", methods=["POST"])
    def diseases_by_age_onsets():
        age_onset_ids = request.json.get('age_onset_ids')
        if not age_onset_ids:
           return utils.create_json_response(jsonify("Age onset IDs are required"), 400)
        
        print(f"Received age onset IDs: {age_onset_ids}")
        # Transform the age onset IDs to include the full URI
        full_age_onset_ids = [f"http://purl.obolibrary.org/obo/{aid}" for aid in age_onset_ids]
        print(f"Transformed age onset IDs: {full_age_onset_ids}")

        diseases = utils.get_diseases_by_age_onsets(full_age_onset_ids, db.get_data_model())
        diseases = utils.convert_objectid_to_str(diseases)
        print(f"Found diseases: {diseases}")
        return utils.create_json_response(jsonify(diseases), 200)

    @app.route("/diseases/by_anatomical_structures", methods=["POST"])
    def diseases_by_anatomical_structures():
        anatomical_ids = request.json.get('anatomical_ids')
        if not anatomical_ids:
            return utils.create_json_response(jsonify("Anatomical structure IDs are required"), 400)
        
        print(f"Received anatomical structure IDs: {anatomical_ids}")
        # Transform the anatomical structure IDs to include the full URI
        full_anatomical_ids = [f"http://purl.obolibrary.org/obo/{aid}" for aid in anatomical_ids]
        print(f"Transformed anatomical structure IDs: {full_anatomical_ids}")

        diseases = utils.get_diseases_by_anatomical_structures(full_anatomical_ids, db.get_data_model())
        diseases = utils.convert_objectid_to_str(diseases)
        print(f"Found diseases: {diseases}")
        return utils.create_json_response(jsonify(diseases), 200)
    
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

        diseases = utils.get_diseases_by_filters(full_phenotype_ids, full_anatomical_ids, full_age_onset_ids, db.get_data_model())
        diseases = utils.convert_objectid_to_str(diseases)
        return utils.create_json_response(jsonify(diseases), 200)

    @app.route("/phenotypes", methods=["GET"])
    def get_phenotypes():
        phenotypes = []
        for disease in db.get_data_model()['diseases']:
            for phenotype in disease.get('phenotypes', []):
                phenotypes.append({
                    "label": phenotype.get('label', 'Unknown Phenotype'),
                    "value": phenotype['target'].replace("http://purl.obolibrary.org/obo/", "")
                })
        
        # Remove duplicates
        unique_phenotypes = {v['value']: v for v in phenotypes}.values()
        return utils.create_json_response(jsonify(list(unique_phenotypes)), 200)

    @app.route("/anatomical_structures", methods=["GET"])
    def get_anatomical_structures():
        anatomical_structures = []
        for disease in db.get_data_model()['diseases']:
            for anatomical_structure in disease.get('anatomical_structures', []):
                anatomical_structures.append({
                    "label": anatomical_structure.get('label', 'Unknown anatomical structure'),
                    "value": anatomical_structure['target'].replace("http://purl.obolibrary.org/obo/", "")
                })
        
        # Remove duplicates
        unique_anatomical_structures = {v['value']: v for v in anatomical_structures}.values()
        return utils.create_json_response(jsonify(list(unique_anatomical_structures)), 200)

    @app.route("/age_onsets", methods=["GET"])
    def get_age_onsets():
        age_onsets = []
        for disease in db.get_data_model()['diseases']:
            for age_onset in disease.get('age_onsets', []):
                age_onsets.append({
                    "label": age_onset.get('label', 'Unknown age onset'),
                    "value": age_onset['target'].replace("http://purl.obolibrary.org/obo/", "")
                })
        
        # Remove duplicates
        unique_age_onsets = {v['value']: v for v in age_onsets}.values()
        return utils.create_json_response(jsonify(list(unique_age_onsets)), 200)
    
    @app.route("/diseases/predict_relationship", methods=["POST"])
    def predict_relationship():

        # new_disease_id = "MONDO_0006781"
        # new_relationship_type = "has_relationship"
        # new_relationship_property = "RO_0004027"
        body = request.json
        disease_id = body.get('disease_id', '')
        new_relationship_type = body.get('new_relationship_type', 'has_relationship')
        new_relationship_property = body.get('new_relationship_property', [])

        # Transform the IDs to include the full URI
        full_disease_id = f"http://purl.obolibrary.org/obo/{disease_id}"
        full_new_relationship_property = f"http://purl.obolibrary.org/obo/{new_relationship_property}"


        predicted_target = utils.predict_relationship(full_disease_id, new_relationship_type, full_new_relationship_property)
        print(f'Predicted target: {predicted_target}')
        
        return utils.create_json_response(jsonify(predicted_target), 200)

    @app.route('/diseases/seen_labels', methods=['GET'])
    def get_seen_labels():
        seen_labels = utils.load_json_from_mongo('seen_labels.json')
        return jsonify(seen_labels)