from bo_drf.serializers import serializer
from chat.api.models import Token


TokenSerializer = serializer('key', model=Token)
