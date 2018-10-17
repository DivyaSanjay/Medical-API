from pymodm import MongoModel, fields
from pymongo.write_concern import WriteConcern

class Symptoms(MongoModel):
    name = fields.CharField()
    id = fields.IntegerField()
    
    class Meta:
        write_concern = WriteConcern(j=True)
        connection_alias = 'my-new-app'

class Issues(MongoModel):
    name = fields.CharField()
    issue_id = fields.IntegerField()
    treatment = fields.CharField()
    possible_symptoms = fields.ListField()
    
    class Meta:
        write_concern = WriteConcern(j=True)
        connection_alias = 'my-new-app'