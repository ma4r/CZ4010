from django.contrib.auth import get_user_model
from rest_framework import serializers
import django.contrib.auth.password_validation as validators
from django.core import exceptions

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username', 'email','id']

class CreateUserSerializer(serializers.Serializer):

    class Meta:
        model = get_user_model()
        fields = ['username', 'email','password']

    def create(self, validated_data):
        return get_user_model()(**validated_data)

    def validate(self, data):
        errors = dict()

        # here data has all the fields which have validated values
        # so we can create a User instance out of it
        user = get_user_model()(**data)
        if get_user_model().objects.filter(username=user.username).exists():
            errors['username'] = "Username is in use"
        if get_user_model().objects.filter(email=user.email).exists():
            errors['email'] = "Email is in use"

        # get the password from the data
        password = data.get('password')
        try:
            # validate the password and catch the exception
            validators.validate_password(password=password, user=user)

        # the exception raised here is different than serializers.ValidationError
        except exceptions.ValidationError as e:
            errors['password'] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

        return super(CreateUserSerializer, self).validate(data)