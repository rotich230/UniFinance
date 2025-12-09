from django.db import models
from django.utils import timezone

# 1. CATEGORY
class Category(models.Model):
    TYPE_CHOICES = [('income', 'Income'), ('expense', 'Expense')]
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='expense')
    limit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self): return self.name

# 2. TRANSACTION
class Transaction(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)

    def __str__(self): return self.description

# 3. SAVINGS GOAL
class SavingsGoal(models.Model):
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_saved = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def progress(self):
        if self.target_amount == 0: return 0
        return int((self.current_saved / self.target_amount) * 100)

    def __str__(self): return self.name

# 4. DEBTS (New!)
class Debt(models.Model):
    DEBT_TYPE = [('owes_me', 'They Owe Me'), ('i_owe', 'I Owe Them')]
    
    person = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=20, choices=DEBT_TYPE)
    date = models.DateField(default=timezone.now)
    is_paid = models.BooleanField(default=False)

    def __str__(self): return f"{self.person} - {self.amount}"