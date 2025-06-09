# expenses/forms.py

from django import forms
from .models import Expense, ExpenseType # Import ExpenseType model
import datetime

class ExpenseTypeForm(forms.ModelForm): # NEW FORM
    class Meta:
        model = ExpenseType
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['expense_type', 'amount', 'expense_date', 'notes']
        widgets = {
            'expense_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate expense_type with ExpenseType objects
        self.fields['expense_type'].queryset = ExpenseType.objects.all().order_by('name') # Dynamically load types
        self.fields['expense_type'].empty_label = "--- Select Expense Type ---" # Optional: add an empty label

        # Apply Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            if field_name == 'expense_type':
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'
        
        # Set default expense_date to today if creating a new expense
        if not self.instance.pk:
            self.fields['expense_date'].initial = datetime.date.today()