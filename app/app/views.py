from django.shortcuts import redirect
from django.http import HttpRequest
import app.constants.template_constants as Templates
from django.contrib.auth import logout, authenticate, login
from app.helpers import authentication
from app.defined_api.mitbih import Arrhythmia
from app.dummies import PatientGenerator
from app.models import Patient

class TemplateView:
    """Built in Template Renderer View Level"""

    def __init__(self):
        pass

    def home(self, request):
        """Renders the home page."""
        
        assert isinstance(request, HttpRequest)

        if not request.user.is_authenticated:
            return redirect("login")
        
        from app.data.reports import GetReports
        report = GetReports()
        
        return Templates.HOME.addContext(report.get_reports()).render_page(request)

    def datasets(self, request):
        """Renders the datasets page."""

        assert isinstance(request, HttpRequest)

        if not request.user.is_authenticated:
            return redirect("login")

        return Templates.DATASETS.render_page(request)
    
    def patients(self, request):
        """Renders the cardiologist page."""

        assert isinstance(request, HttpRequest)
        
        if not request.user.is_authenticated:
            return redirect("login")

        # Make sure it's Cardiologist.
        if not request.user.is_superuser:
            return Templates.PATIENTS.render_page(request)
        else:
            return redirect('home')
        
    def administration(self, request):
        """Renders the admin defined page."""

        assert isinstance(request, HttpRequest)

        if not request.user.is_authenticated:
            return redirect("login")
        
        # Make sure it's Admin.
        if request.user.is_superuser:
            return Templates.ADMINISTRATION.render_page(request)
        else:
            return redirect('home')

    def prescription(self, request, id):
        """Renders the prescription defined page."""

        assert isinstance(request, HttpRequest)

        if not request.user.is_authenticated:
            return redirect("login")
        
        from app.data.prediction_records import PredictionObject

        predictions = PredictionObject()
        prescriptions = predictions.get_records(id)

        return Templates.PRESCRIPTION.addContext(prescriptions).render_page(request)

    def cardiologist(self, request):
        """Renders the cardiologist page."""

        assert isinstance(request, HttpRequest)

        if not request.user.is_authenticated:
            return redirect("login")

        # Make sure it's Cardiologist.
        if not request.user.is_superuser:
            return Templates.CARDIOLOGIST.render_page(request)
        else:
            return redirect('home')
    
    def cardios(self, request):
        """Renders the cardiologist page."""

        assert isinstance(request, HttpRequest)

        if not request.user.is_authenticated:
            return redirect("login")

        # Make sure it's Cardiologist.
        if not request.user.is_superuser:
            return Templates.CARDIOS.render_page(request)
        else:
            return redirect('home')

    def credibility(self, request):
        """Renders the credibility page."""

        assert isinstance(request, HttpRequest)

        if not request.user.is_authenticated:
            return redirect("login")

        return Templates.CREDIBILITY.render_page(request)

    def login(self, request):
        assert isinstance(request, HttpRequest)

        if request.user.is_authenticated == False:
            return Templates.LOGIN.render_page(request)
        return redirect("home")  # Change the home to your index page.

    def user_logout(self, request):
        logout(request)
        return redirect("login")
