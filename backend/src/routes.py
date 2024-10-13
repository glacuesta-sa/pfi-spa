import json
import os
from flask import jsonify, make_response, request
import services
import repository
import utils


from flask_swagger_ui import get_swaggerui_blueprint
def init_routes(app):

    # Swagger UI setup
    SWAGGER_URL = '/v1/docs'
    API_URL = '/.well-known/swagger.yaml'

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,  
        API_URL,     
        config={
            'app_name': "pfi-spa API documentation"
        }
    )

    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    @app.route("/.well-known/swagger.yaml", methods=["GET"])
    def get_swagger_file():
        swagger_file_path = os.path.join(os.path.dirname(__file__), 'doc', 'swagger.yaml')
        print(swagger_file_path)
        with open(swagger_file_path, 'r') as file:
            swagger_yaml = file.read()
        return make_response(swagger_yaml, 200, {'Content-Type': 'application/x-yaml'})

    @app.route("/v1/diseases/<disease_id>", methods=["GET"])
    def get_disease_by_id(disease_id):
        full_id = f"http://purl.obolibrary.org/obo/{disease_id}"
        disease = repository.get_disease_by_id(full_id)
        if disease:
            try:
               services.set_additional_fields(disease)
            except Exception as e:
                return create_json_response(jsonify({"error": str(e)}), 500)

            return create_json_response(jsonify(disease), 200)
        else:
            return create_json_response(jsonify({"error": "Disease not found"}), 404)

    @app.route("/v1/diseases/<disease_id>/hierarchy", methods=["GET"])
    def get_hierarchy_by_id(disease_id):
        full_id = f"http://purl.obolibrary.org/obo/{disease_id}"
        if not repository.get_disease_by_id(full_id):
            return create_json_response(jsonify({"error": "Disease not found"}), 404)
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

        # validate inputs
        #if not (phenotype_ids or anatomical_ids or age_onset_ids or exposure_ids or treatment_ids or chemical_ids):
        #    return create_json_response(jsonify({"error": "no filters received"}), 400) # TODO: generate stub with responses for errors and data structures.
        
        # Transform the IDs to include the full URI
        full_phenotype_ids = [f"http://purl.obolibrary.org/obo/{pid}" for pid in phenotype_ids]
        full_anatomical_ids = [f"http://purl.obolibrary.org/obo/{aid}" for aid in anatomical_ids]
        full_age_onset_ids = [f"http://purl.obolibrary.org/obo/{aid}" for aid in age_onset_ids]
        full_exposure_ids = [f"http://purl.obolibrary.org/obo/{eid}" for eid in exposure_ids]
        full_treatment_ids = [f"http://purl.obolibrary.org/obo/{tid}" for tid in treatment_ids]
        full_chemical_ids = [f"http://purl.obolibrary.org/obo/{cid}" for cid in chemical_ids]

        diseases = services.get_diseases_by_filters(full_phenotype_ids, full_anatomical_ids,
                                                     full_age_onset_ids, full_exposure_ids, full_treatment_ids, full_chemical_ids)
        #for disease in diseases:
        #    services.set_additional_fields(disease)

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

        # validate inputs
        if not (disease_id and new_relationship_type and new_relationship_property):
            return create_json_response(jsonify({"error": "parameters disease_id, new_relationship_type, new_relationship_property are required"}), 400)  # TODO: generate stub with responses for errors and data structures.

        try: 
            # Transform the IDs to include the full URI
            full_disease_id = f"http://purl.obolibrary.org/obo/{disease_id}"
            full_new_relationship_property = f"http://purl.obolibrary.org/obo/{new_relationship_property}"

            predicted_target = services.predict_relationship(full_disease_id, new_relationship_type, full_new_relationship_property)
            print(f'Predicted target: {predicted_target}')

            services.update_data_model(full_disease_id, full_new_relationship_property, predicted_target)
        except Exception as e:
            return create_json_response(jsonify({"error": str(e)}), 500)
        
        return create_json_response(jsonify(predicted_target), 200)

    ################## DEBUG
    @app.route('/diseases/seen_labels', methods=['GET'])
    def get_seen_labels():
        #with repository.fs.get_last_version('seen_labels.json') as file_data:
        #    seen_labels = json.loads(file_data.read().decode('utf-8'))
        #return create_json_response(jsonify({seen_labels}), 200)
         return create_json_response(jsonify({}), 200)
    

def create_json_response(data, status_code=200):
    response = make_response(data, status_code)
    response.headers['Content-Type'] = 'application/json'
    return response