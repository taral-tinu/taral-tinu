# Create your views here.
import ast
import logging
from itertools import chain

from base.models import *
from customer.models import *
from django.contrib.auth.models import User
from django.db.models import (Case, F, Prefetch, Q, Subquery, Value, When,
                              Window)
from django.db.models.aggregates import Count, Sum
from django.db.models.functions.window import FirstValue, LastValue
from django.http.response import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from rest_framework import generics, serializers, status, views, viewsets
from rest_framework.decorators import action, parser_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from sales.models import *
# from finance_api.finance_api import util
from TestProject.rest_config import APIResponse, CustomPagination
from TestProject.util import Util

from .filter import RoleFilter, UserFilter
from .models import (ContentPermission, Group, GroupPermission, MainMenu,
                     PagePermission, UserGroup, UserProfile)

from api.serializer import (RolePermissionSerializer,
                         UserListSerializer, UserProfileSerializer,
                         UserSerializer)


class GetMenus(APIView):
    def get(self, request):
        menu_list = Util.get_cache("menus")
        if menu_list is None:
            menus = MainMenu.objects.filter(parent_id=None, is_active=True).values("id","name","menu_code")
            menu_list = []
            for menu in menus:
                menu_dict = {
                    "name": menu["name"],
                    "code": menu["menu_code"],
                    "ico": "",
                }
                sub_menu = for_sub_menus(menu["id"])

                menu_dict["menu"] = sub_menu
                menu_list.append(menu_dict)
            Util.set_cache("menus", menu_list, 86400)

        return APIResponse(menu_list)


def for_sub_menus(menu_id):
    sub_menu_list = []
    sub_menus = MainMenu.objects.filter(parent_id_id=menu_id).values("id","name","menu_code","url")
    for sub_menu in sub_menus:
        sub_menu_dict = {
            "name": sub_menu["name"],
            "code": sub_menu["menu_code"],
        }
        sub_sub_menu = for_sub_menus(sub_menu["id"])
        if sub_menu["url"]:
            sub_menu_dict["url"] = sub_menu["url"]
        sub_menu_dict["menu"] = sub_sub_menu
        sub_menu_list.append(sub_menu_dict)
    return sub_menu_list

class UserView(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def get_user(self,request):
        user_id = request.data.get("user_id")
        user_role_obj = UserGroup.objects.filter(user_id=user_id).values_list("group_id", flat=True).distinct()
        user_role_obj = ",".join(str(x) for x in user_role_obj)
        user = User.objects.filter(id=user_id).values("first_name","last_name","email","is_active").first()
        serializer = UserSerializer(user)
        user_info ={
            "user_info": serializer.data,
            "user_role_obj":user_role_obj
            }
        return APIResponse(user_info)

    @action(detail=False, methods=['post'])
    def create_user(self,request):
        email = request.data.get("email")
        user_role_ids = request.data.get("role_ids")
        if user_role_ids:
            role_ids = [int(x) for x in user_role_ids.split(",")]
        if email is None:
            return APIResponse(code=0, message="Please Enter Username.")
        if User.objects.filter(email__iexact=email).count() > 0:
            return APIResponse(code=0, message="Email already exists.")
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(username=email)
            UserProfile.objects.create(user_id=serializer.data["id"])
            user_group = [UserGroup(user_id=serializer.data["id"],group_id=group_id) for group_id in role_ids]
            UserGroup.objects.bulk_create(user_group)
            return APIResponse(serializer.data)
        return APIResponse(serializer.errors)

    @action(detail=False, methods=['post'])
    def update_user(self,request):
        user_id = request.data.get('user_id')
        role_ids = request.data.get("role_ids")
        role_ids = [int(x) for x in role_ids.split(",")]
        user = User.objects.get(id=user_id)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            exist_role_ids = UserGroup.objects.filter(user_id=user_id).values_list("group_id", flat=True).distinct()
            user_group = [UserGroup(user=user,group_id=role_id) for role_id in role_ids if role_id not in exist_role_ids]
            delete_role_ids = [x for x in exist_role_ids if x not in role_ids]
            if len(delete_role_ids) > 0:
                UserGroup.objects.filter(user_id=user_id, group_id__in=delete_role_ids).delete()
            UserGroup.objects.bulk_create(user_group)
            return APIResponse(serializer.data)
        return APIResponse(serializer.errors)

    @action(detail=False, methods=['post'])
    def get_profile(self, request):
        user_id = request.data.get("user_id")
        user = UserProfile.objects.filter(user_id=user_id).values("user_id","user__first_name","user__last_name","user__email","profile_image","theme","display_row","default_page").first()
        serializer = UserProfileSerializer(user,context={'request':request})
        return APIResponse(serializer.data)

    @action(detail=False, methods=['post'])
    def save_profile(self, request):
        user_id = int(request.data.get("user_id"))
        user_profile = UserProfile.objects.get(user_id=user_id)
        userprofile_serializer = UserProfileSerializer(user_profile,data=request.data,context={'request':request})
        if userprofile_serializer.is_valid():
            userprofile_serializer.save()
            return APIResponse(userprofile_serializer.data)

        return APIResponse(userprofile_serializer.errors)

    @action(detail=False,methods=['post'])
    def auth_user(self,request):
        username = request.data.get("username")
        user = User.objects.filter(username=username).values("id","is_active").first()
        if user is None:
            return APIResponse(code=0, message="User does not exist in Finance App.")

        if user["is_active"] is False:
            return APIResponse(code=0, message="User is not Active.")

        user = UserProfile.objects.filter(user__username=username).values("user_id","theme","display_row","default_page","profile_image").first()
        serializer = UserProfileSerializer(user,context={'request':request})
        return APIResponse(serializer.data)

class UserListView(generics.ListAPIView):
    queryset = (UserProfile.objects
                .select_related('user')
                .prefetch_related('user__usergroup_set')
                .filter(is_active=True)
                .values("user_id","user__first_name", "user__last_name", "user__username", "user__usergroup__group__name"))

    serializer_class = UserListSerializer
    pagination_class = CustomPagination
    filterset_class = UserFilter

class RoleListView(generics.ListAPIView):
    queryset = Group.objects.values("id","name")
    serializer_class = RolePermissionSerializer
    pagination_class = CustomPagination
    filterset_class = RoleFilter

class UserRole(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def get_role(self , request):
        role_id = request.data.get("role_id")
        list_data = []
        perms = []
        group = Group.objects.filter(id=role_id).values("id","name").first()
        content_permissions = ContentPermission.objects.values("content_group").order_by("sequence")
        for content_permission in content_permissions:
            index = next((index for index, item in enumerate(list_data) if item["content_group"] == content_permission["content_group"]), None)
            if index is None:
                content_name = self.add_perm_list(content_permission["content_group"], [])
                list_data.append({"content_group": content_permission["content_group"] ,"content_name": content_name})

        avail_perms = PagePermission.objects.filter(content__isnull=False).values( "id", "content_id","menu_id", "act_name", "act_code")
        if role_id is not None:
            for lists in list_data:
                for permission in lists["content_name"]:
                    applied_perms = GroupPermission.objects.filter(page_permission__content__id=permission["id"], group_id=group["id"]).values_list("page_permission_id", flat=True)
                    perms = list(chain(perms, applied_perms))
        return APIResponse({"permissions": avail_perms, "applied_perms": perms, "lists": list_data, "group": group})

    def add_perm_list(self,content_group, list_data):
        content_groups = ContentPermission.objects.filter(content_group=content_group).values("id","content_name").order_by("sequence")
        for content_group in content_groups:
            list_data.append({"id": content_group["id"], "content_name": content_group["content_name"]})
        return list_data

    @action(detail=False, methods=['post'])
    def create_and_update_role(self, request):
        user_id = request.data.get("user_id")
        id = request.POST.get("role_id")
        permission_ids = request.data.get("role_perm",None)
        if id is None:
            serializer = RolePermissionSerializer(data=request.data)
        else:
            group = Group.objects.get(id=id)
            serializer = RolePermissionSerializer(group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            group_id = int(serializer.data["id"])
            if permission_ids is not None and len(permission_ids) > 0:
                permissions = []
                new_permissions = [int(x) for x in permission_ids.split(",")]
                role_permissions = (
                        GroupPermission.objects.filter(group_id=group_id, page_permission_id__isnull=False).values_list("page_permission_id", flat=True).distinct()
                    )
                for perm in new_permissions:
                    if perm not in role_permissions:
                        permissions.append(GroupPermission(group_id=group_id, page_permission_id=perm, created_by_id=user_id))
                GroupPermission.objects.bulk_create(permissions)
                perms_to_del =[]
                for perm in role_permissions:
                    if perm not in new_permissions:
                        perms_to_del.append(perm)
                if len(perms_to_del) > 0:
                    GroupPermission.objects.filter(page_permission_id__in=perms_to_del, group_id=group_id).delete()
            # role_data = self.get_role(request)
            # print(role_data.data,"role_data")
            return APIResponse(serializer.data)
        return APIResponse(serializer.errors)

    @action(detail=False, methods=['post'])
    def delete_role(self,request):
        role_ids = request.data["ids"]
        if not role_ids:
            return APIResponse(code = 0, message= "No records selected")
        ids = [int(x) for x in role_ids.split(",")]
        assigned_roles = ""
        roles = UserGroup.objects.filter(group_id__in=ids).values("group__name")

        for role in roles:
            assigned_roles = assigned_roles + role["group__name"] + ", "

        if assigned_roles != "":
            return APIResponse(code=0, message= "'Role "' + {} + '" is assigned to some users. Action cannot be performed. ".format(assigned_roles[:-2]))

        GroupPermission.objects.filter(group_id__in=ids).delete()
        Group.objects.filter(id__in=ids).delete()
        return APIResponse(code=0, message= "Data deleted")

#===================================== collection Action module ===============================#

