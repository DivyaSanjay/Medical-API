import unittest
from models import Symptoms, Issues
from config import *
from server import app

class UnitTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()

    def testFetch_SymptomsAPI(self):
        response = self.app.get('/fetch_symptoms')
        self.assertEqual(response.status_code, 200)

    def testFetch_IssuesAPI(self):
        response = self.app.get('/fetch_issues')
        self.assertEqual(response.status_code, 200)

    def testGet_Medical_ConditionAPI(self):
        response = self.app.get('/get_medical_condition/Anxiety/male/1990')
        self.assertEqual(response.status_code, 200)

    def testGet_Nearby_DoctorsAPI(self):
        response = self.app.get('/get_nearby_doctors/Nucleus Mall, Ranchi')
        self.assertEqual(response.status_code, 200)

    def testTreatmentAPI(self):
        response = self.app.get('/treatment/Flu')
        self.assertEqual(response.status_code, 200)

    def testTell_Your_ProblemAPI(self):
        response = self.app.get("/tell_your_problem/i'm having back pain/female/1989")
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
