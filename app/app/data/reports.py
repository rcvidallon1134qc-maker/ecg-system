from app.models import Patient
from app.models import JsonDataset
from app.models import Cardiologist


class GetReports(object):

    def __init__(self):
        """ A constructor for reports in home. """

        pass

    def get_reports(self):

        count_of_patients = 0 if Patient.objects.all() is None else len(Patient.objects.all())
        count_of_cardiologist = 0 if Cardiologist.objects.all() is None else len(Cardiologist.objects.all())
        count_of_datasets = 0 if JsonDataset.objects.all() is None else len(JsonDataset.objects.all())

        reports = {
            'patients': count_of_patients,
            'cardiologists': count_of_cardiologist,
            'datasets': count_of_datasets
        }

        return reports