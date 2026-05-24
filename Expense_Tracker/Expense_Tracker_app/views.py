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
    



from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .serializers import RegisterSerializer


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Auto-create a token so the user is logged in immediately
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                {
                    'token': token.key,
                    'username': user.username,
                    'email': user.email,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)