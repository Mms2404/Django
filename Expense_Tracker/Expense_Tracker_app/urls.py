from django.urls import path
from .views import ExpenseListCreateView, ExpenseRetrieveUpdateDestroyView


urlpatterns = [
    path('', ExpenseListCreateView.as_view(), name='expense-list-create'),  # GET list / POST create
    path('<int:pk>/', ExpenseRetrieveUpdateDestroyView.as_view(), name='expense-detail'),  # GET/PUT/DELETE expense by id
]


# superuser created ( madhu  , madhu@gmail.com , 123)
# {
#     "username": "Test",
#     "email": "test@example.com",
#     "password": "TestPass123!",
#     "password_confirm": "TestPass123!"
# }