from app.models import Prediction
import pandas as pd
import json
from django.shortcuts import HttpResponse

class ConvertToCSV(object):

    def __init__(self):
        pass

    @staticmethod
    def _get_csv_file(id):
        """ A method to get and download CSV file. """

        result = Prediction.objects.filter(id=id)
        if not result.exists():
            return None  # or raise exception

        for each in result:
            # Load ECG JSON
            ecg_data = json.loads(each.sequential_ecg)

            # Extract values list
            values = ecg_data.get("rates", [])

            # Convert to DataFrame (values as columns)
            df = pd.DataFrame([values])

            # Create HTTP response for CSV download
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="ecg_{id}.csv"'

            df.to_csv(response, index=False)

            return response


        

