from django import forms
from .models import Transaction, SavingsGoal, Budget

# 1. Transaction Form (Add/Edit Expenses)
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['category', 'type', 'amount', 'date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }

# 2. Savings Goal Form (Edit Goals)
class SavingsGoalForm(forms.ModelForm):
    class Meta:
        model = SavingsGoal
        fields = ['name', 'target_amount', 'current_saved']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'target_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'current_saved': forms.NumberInput(attrs={'class': 'form-control'}),
        }

# 3. Budget Limit Form (Edit Monthly Limits) 
class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'limit_amount']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'limit_amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }