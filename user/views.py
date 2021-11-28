from rest_framework import viewsets, status,authentication
from rest_framework.generics import CreateAPIView,ListAPIView
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.request import Request
from .serializers import UserSerializer,CreateUserSerializer
from django.contrib.auth import get_user_model
from rest_framework.authtoken.views import obtain_auth_token
# Create your views here.

class me(ListAPIView):

    def get(self, request, *args, **kwargs):
        # simply delete the token to force a login

        return Response(status=status.HTTP_200_OK,data = {'id':request.user.id})

class Logout(CreateAPIView):

    def post(self, request,*args, **kwargs):
        # simply delete the token to force a login
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)

class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all().order_by('username')
    http_method_names = ['get', 'post']
    permission_classes = []
    def get_serializer_class(self):
        if self.action == 'create' :
            return CreateUserSerializer

        return UserSerializer

    def create(self, request:Request, *args, **kwargs):

        if not(request.auth is None):
            raise APIException(detail="Can't create user",code=status.HTTP_400_BAD_REQUEST)

        serializer = CreateUserSerializer(data=request.data,context={'request':request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        get_user_model().objects.create_user(**serializer.validated_data)

        return Response({"message":"User created sucessfully"},status=status.HTTP_201_CREATED)
