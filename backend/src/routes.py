import json
from flask import jsonify, make_response, request
import services
import repository
import utils

# TODO axel version endpoints
# TODO implement controller-services-repository pattern
def init_routes(app):

    @app.route("/v1/diseases/<disease_id>", methods=["GET"])
    def get_disease_by_id(disease_id):
        full_id = f"http://purl.obolibrary.org/obo/{disease_id}"
        disease = repository.get_disease_by_id(full_id)
        if disease:
            try:
               services.set_llm_fields(disease)
            except Exception as e:
                return create_json_response(jsonify({"error": str(e)}), 500)

            return create_json_response(jsonify(disease), 200)
        else:
            return create_json_response(jsonify("Disease not found"), 404)

    @app.route("/v1/diseases/<disease_id>/hierarchy", methods=["GET"])
    def get_hierarchy_by_id(disease_id):
        full_id = f"http://purl.obolibrary.org/obo/{disease_id}"
        if not repository.get_disease_by_id(full_id):
            return create_json_response(jsonify("Disease not found"), 404)
        hierarchy = services.get_hierarchy_by_disease_id(full_id)

        extended_hierarchy = services.get_extended_hierarchy_by_disease_id(full_id)

        return create_json_response(jsonify({"hierarchy": hierarchy, "extended_hierarchy": extended_hierarchy}), 200)

    @app.route("/v1/diseases/filter", methods=["POST"])
    def get_diseases_by_filters():
        body = request.json
        phenotype_ids = body.get('phenotype_ids', [])
        anatomical_ids = body.get('anatomical_ids', [])
        age_onset_ids = body.get('age_onset_ids', [])
        exposure_ids = body.get('exposure_ids', [])
        treatment_ids = body.get('treatment_ids', [])
        chemical_ids = body.get('chemical_ids', [])
        # include_predictions = body.get('include_predictions', "true")
        
        # Transform the IDs to include the full URI
        full_phenotype_ids = [f"http://purl.obolibrary.org/obo/{pid}" for pid in phenotype_ids]
        full_anatomical_ids = [f"http://purl.obolibrary.org/obo/{aid}" for aid in anatomical_ids]
        full_age_onset_ids = [f"http://purl.obolibrary.org/obo/{aid}" for aid in age_onset_ids]
        full_exposure_ids = [f"http://purl.obolibrary.org/obo/{eid}" for eid in exposure_ids]
        full_treatment_ids = [f"http://purl.obolibrary.org/obo/{tid}" for tid in treatment_ids]
        full_chemical_ids = [f"http://purl.obolibrary.org/obo/{cid}" for cid in chemical_ids]

        diseases = services.get_diseases_by_filters(full_phenotype_ids, full_anatomical_ids,
                                                     full_age_onset_ids, full_exposure_ids, full_treatment_ids, full_chemical_ids)
        diseases = utils.convert_objectid_to_str(diseases)
        return create_json_response(jsonify(diseases), 200)

    @app.route("/v1/phenotypes", methods=["GET"])
    def get_phenotypes():
        return create_json_response(jsonify(services.get_phenotypes()), 200)
    
    @app.route("/v1/anatomical_structures", methods=["GET"])
    def get_anatomical_structures():
        return create_json_response(jsonify(services.get_anatomical_structures()), 200)

    @app.route("/v1/age_onsets", methods=["GET"])
    def get_age_onsets():
        return create_json_response(jsonify(services.get_age_onsets()), 200)
    
    @app.route("/v1/exposures", methods=["GET"])
    def get_exposures():
        return create_json_response(jsonify(services.get_exposures()), 200)
    
    @app.route("/v1/treatments", methods=["GET"])
    def get_etreatments():
        return create_json_response(jsonify(services.get_treatments()), 200)
    
    @app.route("/v1/chemicals", methods=["GET"])
    def get_chemicals():
        return create_json_response(jsonify(services.get_chemicals()), 200)
    
    @app.route("/v1/relationship_types", methods=["GET"])
    def get_relationship_types():
        return create_json_response(jsonify(services.get_relationship_types()), 200)
    
    @app.route("/v1/diseases/predict", methods=["POST"])
    def get_disease_prediction():

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

        predicted_target = services.predict_relationship(full_disease_id, new_relationship_type, full_new_relationship_property)
        print(f'Predicted target: {predicted_target}')

        services.update_data_model(full_disease_id, full_new_relationship_property, predicted_target)
        
        return create_json_response(jsonify(predicted_target), 200)

    ################## DEBUG
    @app.route('/diseases/seen_labels', methods=['GET'])
    def get_seen_labels():
        with repository.fs.get_last_version('seen_labels.json') as file_data:
            seen_labels = json.loads(file_data.read().decode('utf-8'))
        return create_json_response(jsonify(seen_labels), 200)
    

def create_json_response(data, status_code=200):
    response = make_response(data, status_code)
    response.headers['Content-Type'] = 'application/json'
    return response