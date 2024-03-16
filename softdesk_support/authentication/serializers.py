from rest_framework.serializers import ModelSerializer

from authentication.models import User

class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = [
            'username',
            'created_time',
            'age',
            'can_be_contacted',
            'can_data_be_shared'
        ]