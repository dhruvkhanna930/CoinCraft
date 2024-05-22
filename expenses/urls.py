from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    path('', views.index, name="expenses"),
    path('add-expense/', views.add_expense, name="add-expenses"),
    path('edit-expense/<int:id>', views.edit_expense, name="edit-expenses"),
    path('delete-expense/<int:id>', views.delete_expense, name="delete-expenses"),
    path('search-expense/', csrf_exempt(views.search_expense), name="search-expenses"),

    path('expense-category-summary/', csrf_exempt(views.expense_category_summary), name="expense-category-summary"),
    path('stats/', views.stats_view, name="stats"),
]