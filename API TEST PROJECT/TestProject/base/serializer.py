from dataclasses import fields

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework import serializers

from base.models import CodeTable


class CodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeTable
        fields = "__all__"

class BulkListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        # print(validated_data,"LL")
        result = [self.child.create(attrs) for attrs in validated_data]
        try:
            self.child.Meta.model.objects.bulk_create(result)
        except IntegrityError as e:
            raise ValidationError(e)
        return result

    # def update(self, instances, validated_data):
    #     # print("validated_data",validated_data)
    #     instance_hash = {index: instance for index, instance in enumerate(instances)}
    #     result = [
    #         self.child.update(instance_hash[index], attrs)
    #         for index, attrs in enumerate(validated_data)
    #     ]
    #     writable_fields = [
    #         x
    #         for x in self.child.Meta.fields
    #     ]
    #     try:
    #         self.child.Meta.model.objects.bulk_update(result, writable_fields)
    #     except IntegrityError as e:
    #         raise ValidationError(e)
        return result
