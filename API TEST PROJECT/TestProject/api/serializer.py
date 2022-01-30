import ast
from tokenize import group
from urllib import request

from base.models import *
from base.models import CodeTable, Currency
from customer.models import *
from django.contrib.auth.models import Group, User
from django.db.models.signals import pre_save
from django.forms import fields
from rest_framework import serializers
# from TestProject.signals import DeleteOldFile

from TestProject.rest_config import LocalDateTime, RepresentFilePath
from TestProject.util import Util

from .models import UserGroup, UserProfile


class RolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id","name"]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name","is_active"]

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    profile_image = RepresentFilePath(required=False)
    class Meta:
        model = UserProfile
        fields = ["user","profile_image","theme","display_row","default_page"]

    def update(self,instance,validated_data):
        user_data = validated_data.pop("user")
        user_serializer = self.fields['user']
        if "profile_image" in validated_data:
            Util.delete_old_file(instance.profile_image.path)
        user_serializer.update(instance.user,user_data)
        return super().update(instance, validated_data)


class UserRoleSerializer(serializers.ModelSerializer):
    role_ids = serializers.ListField(write_only=True)
    class Meta:
        model = User
        fields = ("first_name","last_name","email","is_active","role_ids")

    def create(self, validated_data):
        role_ids = validated_data.pop("role_ids")
        user = User.objects.create(**validated_data)
        user_group = [UserGroup(user=user,group_id=group_id) for group_id in role_ids]
        UserGroup.objects.bulk_create(user_group)
        return user

class UserListSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user__first_name')
    last_name = serializers.CharField(source='user__last_name')
    username = serializers.CharField(source='user__username')
    usergroup = serializers.CharField(source='user__usergroup__group__name',read_only=True)
    roles = serializers.ListField(write_only=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email","username","is_active","usergroup","roles"]
