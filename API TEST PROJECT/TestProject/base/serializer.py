from dataclasses import fields

from rest_framework import serializers

from base.models import CodeTable


class CodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeTable
        fields = "__all__"

