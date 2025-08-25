from app.models import Prediction
from datetime import date

class PredictionObject(object):

    def __init__(self):
        """ This class is for ORM object of prediction model(s) """
        pass

    def get_records(self, id):
        """ A method to get Prediction object. """
        
        results = Prediction.objects.all().filter(id = id)

        if results:

            for patient in results:

                age = date.today().year - patient.patient.birth.year
                attending_physician = str(patient.attending_physician.user.first_name) + " " + str(patient.attending_physician.user.last_name) + " " + str(patient.attending_physician.suffixes)
                e_signature = 'media/' + str(patient.attending_physician.e_signature)
            
                return {
                    'recommendations': patient.recommendations,
                    'patient_name': str(patient.patient.first_name) + " " + str(patient.patient.middle_name) + " " + str(patient.patient.last_name),
                    'remarks': patient.remarks,
                    'age': age,
                    'attending_physician': attending_physician,
                    'e_signature': e_signature,
                    'date': date.today()
                }
            
            return {
                'recommendations': '',
                'patient_name': '',
                'remarks': '',
                'age': 0,
                'attending_physician': '',
                'e_signature': '',
                'date': date.today()
            }