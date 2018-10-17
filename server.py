import requests
import hmac, hashlib
import base64
import json
from pymodm.connection import connect
from config import *
from models import Symptoms, Issues
import googlemaps
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from rasa_nlu.training_data import load_data
from rasa_nlu.config import RasaNLUModelConfig
from rasa_nlu.model import Trainer

config_rasa = RasaNLUModelConfig(configuration_values = {"pipeline":[{ "name": "nlp_spacy" },{ "name": "tokenizer_spacy" },
                                                   { "name": "intent_entity_featurizer_regex" },{ "name": "intent_featurizer_spacy"},
                                                   { "name": "ner_crf" },{ "name": "ner_synonyms" },{ "name": "intent_classifier_sklearn" },
                                                   { "name": "ner_spacy" }]})
trainer = Trainer(config_rasa)
training_data = load_data("training_data.json")
interpreter = trainer.train(training_data)

connect("mongodb://localhost:27017/Apimedic2", alias="my-new-app")
gmaps = googlemaps.Client(key='AIzaSyCmkg7endJg0r41QVpEmCx19eK2fhLVeVc')

def generate_token():
    rawString = hmac.new(bytes(password, encoding='utf-8'), priaid_authservice_url.encode('utf-8')).digest()
    hashString = base64.b64encode(rawString).decode()
    credentials = username + ':' + hashString
    header = {
        'Authorization': 'Bearer {}'.format(credentials)
    }
    response = requests.post(priaid_authservice_url, headers=header)
    data = json.loads(response.text)
    extraArgs = "token=" + data['Token'] + "&format=json&language=" + language
    return extraArgs

app = Flask(__name__)
api = Api(app)

def calculate_ids(symptoms):
    ids = []
    for s in symptoms:
        query = list(Symptoms.objects.raw({'name':s}))
        for i in query:
            ids.append(i.id)
    return ids

def calculate_med_conds(issue_ids, extraArgs):
    med_conds = []
    for issue_id in issue_ids:
        url = priaid_healthservice_url+'/issues/'+str(issue_id)+'/info?'+extraArgs
        response = requests.get(url)
        data = json.loads(response.text)
        med_conds.append({'Name':data['Name'], 'Condition':data['MedicalCondition']})
        return med_conds

class Fetch_Symptoms(Resource):
    def get(self):
        extraArgs = generate_token()
        if Symptoms.objects.count() == 0:
            url = priaid_healthservice_url + '/symptoms?' + extraArgs 
            response = requests.get(url)
            results = json.loads(response.text)
            for i in results:
                Symptoms(name=i['Name'], id=i['ID']).save()
        else:
            query = list(Symptoms.objects.all())
            results = []
            for i in query:
                results.append({'ID':i.id,'Name':i.name})
        return jsonify(200,{'Results':results})

class Get_Medical_Condition(Resource):
    def get(self, symptoms, gender, year):
        extraArgs = generate_token()
        symptoms = symptoms.split(',')
        ids = calculate_ids(symptoms)
        url = priaid_healthservice_url+'/diagnosis?'+extraArgs+'&symptoms='+json.dumps(ids)+'&gender='+gender+'&year_of_birth='+str(year)
        response = requests.get(url)
        data = json.loads(response.text)
        issue_ids = [i['Issue']['ID'] for i in data if i['Issue']['Accuracy']>25]
        med_conds = calculate_med_conds(issue_ids, extraArgs)
        return jsonify(200,{'Results': med_conds})

class Tell_Your_Problem(Resource):
    def get(self, problem, gender, year):
        extraArgs = generate_token()
        parse_data = interpreter.parse(problem)
        entities = parse_data['entities']
        symptoms = [ent['value'] for ent in entities]
        ids = calculate_ids(symptoms)
        url = priaid_healthservice_url+'/diagnosis?'+extraArgs+'&symptoms='+json.dumps(ids)+'&gender='+gender+'&year_of_birth='+str(year)
        response = requests.get(url)
        data = json.loads(response.text)
        issue_ids = [i['Issue']['ID'] for i in data if i['Issue']['Accuracy']>25]
        med_conds = calculate_med_conds(issue_ids, extraArgs)
        return jsonify(200,{'Results': med_conds})

issues = []
class Treatment(Resource):
    def get(self, issue):
        extraArgs = generate_token()
        print(issues)
        if issue in issues:
            query = list(Issues.objects.raw({'name':issue}))
            results = [{'Medical Condition':i.name, 'Treatment':i.treatment} for i in query]
            return jsonify(200,{'Results': results})
        else:
            issues.append(issue)
            query = list(Issues.objects.raw({'name':issue}))
            issue_ids = [i.issue_id for i in query]
            med_conds = []
            for issue_id in issue_ids:
                url = priaid_healthservice_url+'/issues/'+str(issue_id)+'/info?'+extraArgs
                response = requests.get(url)
                data = json.loads(response.text)
                Issues.objects.raw({'issue_id':issue_id}).update(
                    {"$set": {"treatment":data['TreatmentDescription'], "possible_symptoms":data['PossibleSymptoms']}},
                    upsert = True)
                med_conds.append({'MedicalCondition':data['Name'], 'Treatment':data['TreatmentDescription']})
            return jsonify(200,{'Results': med_conds})

class Fetch_Issues(Resource):
    def get(self):
        extraArgs = generate_token()
        if Issues.objects.count() == 0:
            url = priaid_healthservice_url+'/issues?'+extraArgs
            response = requests.get(url)
            data = json.loads(response.text)
            for i in data:
                Issues(name=i['Name'],issue_id=i['ID'],treatment='NA',possible_symptoms='NA').save()
        query = list(Issues.objects.all())
        results = []
        for i in query:
            results.append({'Name':i.name})
        return jsonify(200,{'Results':results})

class Get_Nearby_Doctors(Resource):
    def get(self, address):
        extraArgs = generate_token()
        geocode_result = gmaps.geocode(address)
        latitude = geocode_result[0]['geometry']['location']['lat']
        longitude = geocode_result[0]['geometry']['location']['lng']
        location = gmaps.places_nearby(location=(latitude, longitude), radius=10000, type='doctor')
        response = [{'name': result['name'], 'address': result['vicinity']} for result in location['results']]
        return jsonify(200,{'results': response})

api.add_resource(Fetch_Symptoms, '/fetch_symptoms') # API 1
api.add_resource(Get_Medical_Condition, '/get_medical_condition/<symptoms>/<gender>/<year>') # API 2
api.add_resource(Tell_Your_Problem, '/tell_your_problem/<problem>/<gender>/<year>') # API 5
api.add_resource(Treatment, '/treatment/<issue>') # API 3
api.add_resource(Fetch_Issues, '/fetch_issues') # API to fetch the issues for user reference
api.add_resource(Get_Nearby_Doctors, '/get_nearby_doctors/<address>') # API 4

if __name__ == '__main__':
    app.run(port='5002', debug=True)
