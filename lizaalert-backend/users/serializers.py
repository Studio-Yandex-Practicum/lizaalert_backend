from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Badge, Location, Volunteer

User = get_user_model()


class BageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ['name', 'description', ]


class FullNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'patronymic']

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name',
                                                 instance.first_name)
        instance.last_name = validated_data.get('last_name',
                                                instance.last_name)
        instance.patronymic = validated_data.get('patronymic',
                                                 instance.patronymic)
        instance.save()
        return instance


class VolunteerSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    location = serializers.CharField(required=False,
                                     allow_null=True,
                                     source='location.region')
    full_name = FullNameSerializer(source='user')
    photo = serializers.SerializerMethodField(read_only=True)
    level = serializers.CharField(source='level.name', read_only=True)
    badges = BageSerializer(many=True, read_only=True)
    count_pass_course = serializers.IntegerField(read_only=True)

    class Meta:
        model = Volunteer
        fields = ['id', 'phone_number', 'email', 'full_name',
                  'birth_date', 'location', 'call_sign', 'photo', 'level',
                  'badges', 'count_pass_course'
                  ]

    def get_photo(self, obj):
        request = self.context.get('request')
        if obj.photo:
            photo_url = obj.photo.url
            return request.build_absolute_uri(photo_url)
        return None

    def update(self, instance, validated_data):
        instance.birth_date = validated_data.get('birth_date',
                                                 instance.birth_date)
        instance.call_sign = validated_data.get('call_sign',
                                                instance.call_sign)
        instance.phone_number = validated_data.get('phone_number',
                                                   instance.phone_number)

        location = validated_data.get('location', None)
        if location and (
            Location.objects.filter(region=location['region']).exists()
        ):
            region = Location.objects.get(region=location['region'])
            print(region)
            instance.location = Location.objects.get(region=location['region'])

        full_name = validated_data.get('user', None)
        if full_name:
            serializer = FullNameSerializer(
                instance.user, data=full_name, partial=True
            )
            if serializer.is_valid():
                serializer.save()
        instance.save()
        return instance
