from rest_framework import generics , permissions
from .serializers import ExpenseSerializer
from .models import Expense 

# Create your views here.

class ExpenseListView(generics.ListAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        print(queryset)
        return queryset

# List and Create expenses, user-specific
class ExpenseListCreateView(generics.ListCreateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # only returns expenses belonging to the logged-in user
        return Expense.objects.filter(user = self.request.user).order_by('date')
    
    def perform_create(self, serializer):
        # setting the logged-in user as the expense owner
        serializer.save(user=self.request.user)


# Retrieve, Update, or Delete a specific expense
class ExpenseRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]


    def get_queryset(self):
        # nnly allows access to the logged-in user's expenses
        return Expense.objects.filter(user=self.request.user)