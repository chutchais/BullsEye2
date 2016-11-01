from django.db import models
from django import forms 
from django.forms.models import inlineformset_factory
from django.forms import ModelForm,Textarea
from .models import Station,Product,Family,Parameter
from .models import Bom,BomDetails

class StationModelForm(forms.ModelForm):
    def clean_station(self):
	    if False:
	        raise forms.ValidationError("Station must be number")
	    return self.cleaned_data["station"]

    class Meta:
        model = Station
        fields = ('station','name','family','description',)
        widgets = {
	            'description': Textarea(attrs={'cols': 50, 'rows': 10}),
	            }


class BomForm(forms.ModelForm):
    class Meta:
    	model = Bom
    	fields = ('name','model','rev',)


BomDetailsFormSet = inlineformset_factory(Bom, BomDetails,fields=("pn", "rd"))



class DashboardForm(forms.Form):
    report_date = forms.DateField(label='Date', input_formats=['%Y-%m-%d'])#, initial=date.today

class snTrackingForm(forms.Form):
    sn = forms.CharField(label='Serial number')


#For SPC Main
class ReportFiltersForm(forms.Form):
    start_date = forms.DateField(label='Start Date',input_formats=['%Y-%m-%d'])
    end_date = forms.DateField(label='End Date',input_formats=['%Y-%m-%d'])
#,widget=SelectDateWidget()

#For SPC selection
class SpcFilterForm(forms.Form):
    start_date = forms.DateField(label='Start Date',input_formats=['%Y-%m-%d'])
    end_date = forms.DateField(label='End Date',input_formats=['%Y-%m-%d'])
    family = forms.ModelChoiceField(queryset=Family.objects.all(), empty_label="(ALL)")#forms.CharField(label='Product Family')
    # station = forms.ModelChoiceField(queryset=Station.objects.all(),
    # to_field_name="name", empty_label="(ALL)")#forms.CharField(label='Station')
    station = forms.ModelChoiceField(queryset=Station.objects.none())
    parameter = forms.ModelChoiceField(queryset=Parameter.objects.none(),
    to_field_name="name", empty_label="(ALL)")#forms.CharField(label='Station')
    product = forms.ModelMultipleChoiceField(queryset=Product.objects.none()) #forms.CharField(label='Product') 

    def __init__(self, *args, **kwargs):
        super(SpcFilterForm, self).__init__(*args, **kwargs)
        # access object through self.instance...
        #self.fields['station'].queryset = Station.objects.filter(family='CFP')
        #self.fields['station'].choices = list(Station.objects.values_list('station', 'name'))
        #self.fields['books'].choices = list(Books.objects.values_list('id', 'name'))

#TypedChoiceField
#ModelChoiceField