from django import forms
from .models import Report, Residence


class ReportForm(forms.ModelForm):
    TYPE_CHOICES = (
        ('', '--- Select Report Type ---'),  # Add an empty choice
        ('Noise Complaint', 'Noise Complaint'),
        ('Maintenance Request', 'Maintenance Request'),
        ('Neighbor/Roommate Dispute', 'Neighbor/Roommate Dispute'),
        ('Safety Concern', 'Safety Concern'),
        ('Substance Abuse Concern', 'Substance Abuse Concern'),
        ('Suspicious Activity', 'Suspicious Activity'),
        ('Rule Violation', 'Rule Violation'),
        ('Other', 'Other'),

    )

    report_type = forms.ChoiceField(choices=TYPE_CHOICES, required=True)

    class Meta:
        model = Report
        fields = ['report_type', 'report_text', 'report_file', 'building', 'floor', 'room']
        widgets = {
            'report_file': forms.ClearableFileInput(),
        }

    def __init__(self, *args, **kwargs):
        selected_residence = kwargs.pop('selected_residence', None)
        super(ReportForm, self).__init__(*args, **kwargs)
        if selected_residence:
            buildings = Residence.objects.filter(residence=selected_residence).values_list('building',
                                                                                           flat=True).distinct()
            choices = [(building, building) for building in buildings]
            # Add an empty choice to the beginning of the choices list
            choices.insert(0, ('', '--- Select Building ---'))
            self.fields['building'].widget = forms.Select(choices=choices)
            # Disable dropdown if there's only one building
        # if len(buildings) == 1:
        #     self.fields['building'].widget.attrs['disabled'] = 'disabled'


