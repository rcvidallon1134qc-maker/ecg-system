from app.models import Patient
from app.models import JsonDataset
from app.models import Cardiologist
from app.models import Prediction
from django.db.models import Count, Q
from collections import Counter
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class GetReports(object):

    def __init__(self):
        """ A constructor for reports in home. """

        pass

    def get_reports(self):

        count_of_patients = 0 if Patient.objects.all() is None else len(Patient.objects.all())
        count_of_cardiologist = 0 if Cardiologist.objects.all() is None else len(Cardiologist.objects.all())
        count_of_datasets = 0 if JsonDataset.objects.all() is None else len(JsonDataset.objects.all())
        count_of_predictions = Prediction.objects.count()

        # Arrhythmia analytics
        arrhythmia_data = self.get_arrhythmia_analytics()
        
        # Age demographics
        age_demographics = self.get_age_demographics()

        reports = {
            'patients': count_of_patients,
            'cardiologists': count_of_cardiologist,
            'datasets': count_of_datasets,
            'predictions': count_of_predictions,
            'arrhythmia_analytics': arrhythmia_data,
            'age_demographics': age_demographics
        }

        return reports

    def get_arrhythmia_analytics(self):
        """Get arrhythmia type distribution by age groups and months with patient details"""
        
        # Get all predictions with patient data
        all_predictions = Prediction.objects.select_related('patient').filter(
            patient__isnull=False,
            patient__birth__isnull=False
        )
        
        # Get data for the last 6 months
        today = date.today()
        six_months_ago = today - relativedelta(months=6)
        
        # Data structure: {month: {age_group: {arrhythmia: [patient_details]}}}
        monthly_age_arrhythmia = {}
        
        # Age groups definition
        age_groups_ranges = [
            ('0-20', 0, 20),
            ('21-40', 21, 40),
            ('41-60', 41, 60),
            ('61-80', 61, 80),
            ('81+', 81, 200)
        ]
        
        # Process each prediction
        for pred in all_predictions:
            # Skip if no creation date (use current date as fallback)
            pred_date = pred.created_at.date() if pred.created_at else today
            
            # Only include last 6 months
            if pred_date < six_months_ago:
                continue
            
            # Get month-year key
            month_key = pred_date.strftime('%B %Y')  # e.g., "November 2025"
            
            # Calculate patient age
            birth_date = pred.patient.birth
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            # Determine age group
            age_group = '81+'
            for group_name, min_age, max_age in age_groups_ranges:
                if min_age <= age <= max_age:
                    age_group = group_name
                    break
            
            # Get arrhythmia type
            arrhythmia = pred.arrhythmia_type if pred.arrhythmia_type else pred.remarks
            if not arrhythmia or arrhythmia.strip() == '':
                arrhythmia = 'Unknown'
            
            # Initialize nested structure if needed
            if month_key not in monthly_age_arrhythmia:
                monthly_age_arrhythmia[month_key] = {}
            if age_group not in monthly_age_arrhythmia[month_key]:
                monthly_age_arrhythmia[month_key][age_group] = {}
            if arrhythmia not in monthly_age_arrhythmia[month_key][age_group]:
                monthly_age_arrhythmia[month_key][age_group][arrhythmia] = []
            
            # Add patient details with age display
            patient_name = f"{pred.patient.first_name} {pred.patient.last_name}"
            
            # Calculate age display (years or months for infants)
            if age < 1:
                # Calculate months for infants
                months = (today.year - birth_date.year) * 12 + today.month - birth_date.month
                if today.day < birth_date.day:
                    months -= 1
                age_display = f"{months} mo" if months > 0 else "< 1 mo"
            else:
                age_display = f"{age} yr{'s' if age != 1 else ''}"
            
            monthly_age_arrhythmia[month_key][age_group][arrhythmia].append({
                'name': patient_name,
                'age': age_display,
                'date': pred_date.strftime('%b %d, %Y'),
                'id': pred.patient.id
            })
        
        # Sort months chronologically (most recent first)
        sorted_months = sorted(
            monthly_age_arrhythmia.keys(),
            key=lambda x: datetime.strptime(x, '%B %Y'),
            reverse=True
        )
        
        # Format data for template
        monthly_data = []
        total_patients = 0
        
        for month in sorted_months:
            age_data = []
            month_total = 0
            
            for age_group in ['0-20', '21-40', '41-60', '61-80', '81+']:
                if age_group in monthly_age_arrhythmia[month]:
                    arrhythmia_breakdown = []
                    group_total = 0
                    
                    for arrhythmia, patients in monthly_age_arrhythmia[month][age_group].items():
                        arrhythmia_breakdown.append({
                            'type': arrhythmia,
                            'count': len(patients),
                            'patients': patients
                        })
                        group_total += len(patients)
                    
                    # Sort by count
                    arrhythmia_breakdown.sort(key=lambda x: x['count'], reverse=True)
                    
                    age_data.append({
                        'age_group': age_group,
                        'total': group_total,
                        'arrhythmias': arrhythmia_breakdown
                    })
                    month_total += group_total
            
            if age_data:  # Only add months with data
                monthly_data.append({
                    'month': month,
                    'age_groups': age_data,
                    'total': month_total
                })
                total_patients += month_total
        
        return {
            'monthly_data': monthly_data,
            'total_patients': total_patients,
            'has_data': len(monthly_data) > 0
        }

    def get_age_demographics(self):
        """Get age distribution of patients"""
        
        # Get all patients with birth date
        patients = Patient.objects.exclude(birth__isnull=True)
        
        # Age groups
        age_groups = {
            '0-20': 0,
            '21-40': 0,
            '41-60': 0,
            '61-80': 0,
            '81+': 0
        }
        
        # Calculate ages from birth date
        today = date.today()
        ages = []
        
        for patient in patients:
            # Calculate age from birth date
            birth_date = patient.birth
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            ages.append(age)
            
            # Categorize into age groups
            if age <= 20:
                age_groups['0-20'] += 1
            elif age <= 40:
                age_groups['21-40'] += 1
            elif age <= 60:
                age_groups['41-60'] += 1
            elif age <= 80:
                age_groups['61-80'] += 1
            else:
                age_groups['81+'] += 1
        
        # Calculate average age
        avg_age = sum(ages) / len(ages) if ages else 0
        
        return {
            'age_groups': age_groups,
            'labels': list(age_groups.keys()),
            'values': list(age_groups.values()),
            'average_age': round(avg_age, 1),
            'total_with_age': len(ages)
        }