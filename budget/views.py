from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Transaction, Category, SavingsGoal, Debt
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

# ==========================================
# 1. DASHBOARD (Overview)
# ==========================================
@login_required
def dashboard(request):
    # Calculate Totals based on Category Type
    income = Transaction.objects.filter(category__type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    expense = Transaction.objects.filter(category__type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Balance = Income - Expenses
    balance = income - expense

    # Get only the 5 most recent transactions for the "Quick Look" table
    recent_transactions = Transaction.objects.all().order_by('-date')[:5]

    context = {
        'income': income,
        'expense': expense,
        'balance': balance,
        'recent_transactions': recent_transactions
    }
    return render(request, 'dashboard.html', context)


# ==========================================
# 2. FINANCE MANAGER (With Edit Logic)
# ==========================================
@login_required 
def finance_manager(request):
    if request.method == "POST":
        action = request.POST.get('action')

        # A. ADD CATEGORY
        if action == 'add_category':
            Category.objects.create(
                name=request.POST.get('cat_name'), 
                limit=request.POST.get('cat_limit'), 
                type=request.POST.get('cat_type')
            )

        # B. DELETE CATEGORY
        elif action == 'delete_category':
            Category.objects.filter(id=request.POST.get('category_id')).delete()

        # C. ADD TRANSACTION
        elif action == 'add_transaction':
            cat = Category.objects.get(id=request.POST.get('category_id'))
            raw_amount = Decimal(request.POST.get('amount'))
            date = request.POST.get('date')
            desc = request.POST.get('description')
            
            Transaction.objects.create(description=desc, amount=raw_amount, date=date, category=cat)

            # Auto-Save Logic (20%)
            if cat.type == 'income':
                saving_cut = raw_amount * Decimal('0.20')
                goal = SavingsGoal.objects.filter(name__icontains="Savings").first()
                if not goal: goal = SavingsGoal.objects.first() 
                if goal:
                    goal.current_saved += saving_cut
                    goal.save()
                    save_cat, _ = Category.objects.get_or_create(name="Savings Transfer", defaults={'type': 'expense', 'limit': 0})
                    Transaction.objects.create(description=f"Auto-Save (20% of {desc})", amount=saving_cut, date=date, category=save_cat)

        # D. EDIT TRANSACTION (NEW!)
        elif action == 'edit_transaction':
            # Get the existing transaction
            t = get_object_or_404(Transaction, id=request.POST.get('transaction_id'))
            
            # Update fields with new data
            t.description = request.POST.get('description')
            t.amount = Decimal(request.POST.get('amount'))
            t.date = request.POST.get('date')
            t.category = Category.objects.get(id=request.POST.get('category_id'))
            
            t.save()

        # E. DELETE TRANSACTION
        elif action == 'delete_transaction':
            Transaction.objects.filter(id=request.POST.get('transaction_id')).delete()
        
        return redirect('finance_manager')

    # Load Data (Monthly Filter)
    now = timezone.now()
    transactions = Transaction.objects.select_related('category').order_by('-date')
    categories = Category.objects.all()

    for cat in categories:
        spent = Transaction.objects.filter(category=cat, date__year=now.year, date__month=now.month).aggregate(Sum('amount'))['amount__sum'] or 0
        cat.spent = spent
        if cat.limit > 0 and cat.type == 'expense':
            percentage = (spent / cat.limit) * 100
            cat.percent = int(percentage)
            if percentage >= 100: cat.status, cat.color = 'DANGER', 'bg-danger'
            elif percentage >= 75: cat.status, cat.color = 'WARNING', 'bg-warning'
            else: cat.status, cat.color = 'SAFE', 'bg-success'
        else:
            cat.percent, cat.status, cat.color = 0, '---', 'bg-secondary'

    return render(request, 'finance_manager.html', {'transactions': transactions, 'categories': categories, 'month_name': now.strftime('%B')})


# ==========================================
# 3. SAVINGS GOALS
# ==========================================
@login_required
def savings_view(request):
    if request.method == "POST":
        action = request.POST.get('action')
        
        # A. Add Goal
        if action == 'add_goal':
            SavingsGoal.objects.create(
                name=request.POST.get('goal_name'), 
                target_amount=request.POST.get('target_amount'), 
                current_saved=request.POST.get('current_saved') or 0
            )
        
        # B. Delete Goal
        elif action == 'delete_goal':
            SavingsGoal.objects.filter(id=request.POST.get('goal_id')).delete()
        
        # C. Deposit Money
        elif action == 'deposit':
            goal = get_object_or_404(SavingsGoal, id=request.POST.get('goal_id'))
            goal.current_saved += Decimal(request.POST.get('amount'))
            goal.save()
            
        return redirect('savings_view')
    
    goals = SavingsGoal.objects.all()
    return render(request, 'savings.html', {'goals': goals})


# ==========================================
# 4. DEBTS & LENDING (The New Page)
# ==========================================
@login_required
def debt_view(request):
    if request.method == "POST":
        action = request.POST.get('action')
        
        # A. Add Debt
        if action == 'add_debt':
            Debt.objects.create(
                person=request.POST.get('person'),
                amount=request.POST.get('amount'),
                type=request.POST.get('type'),
                date=request.POST.get('date')
            )
        
        # B. Mark as Paid
        elif action == 'mark_paid':
            debt = get_object_or_404(Debt, id=request.POST.get('debt_id'))
            debt.is_paid = True
            debt.save()
            
        # C. Delete Record
        elif action == 'delete_debt':
            Debt.objects.filter(id=request.POST.get('debt_id')).delete()
            
        return redirect('debt_view')

    # Separate lists for display
    owes_me = Debt.objects.filter(type='owes_me', is_paid=False)
    i_owe = Debt.objects.filter(type='i_owe', is_paid=False)
    
    return render(request, 'debts.html', {'owes_me': owes_me, 'i_owe': i_owe})

# ==========================================
# 5. USER REGISTRATION (Sign Up)
# ==========================================
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in immediately after signing up
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})