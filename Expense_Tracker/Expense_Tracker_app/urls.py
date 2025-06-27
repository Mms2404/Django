from django.urls import path
from .views import ExpenseListCreateView, ExpenseRetrieveUpdateDestroyView


urlpatterns = [
    path('', ExpenseListCreateView.as_view(), name='expense-list-create'),  # GET list / POST create
    path('<int:pk>/', ExpenseRetrieveUpdateDestroyView.as_view(), name='expense-detail'),  # GET/PUT/DELETE expense by id
]


# super user created ( madhu  , madhu@gmail.com , 123)