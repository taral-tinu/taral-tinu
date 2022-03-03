import ast
import datetime
import json
import logging
import re
from itertools import chain
from posixpath import split

import requests
from base.models import *
from base.util import Util
from customer.models import *
from customer.models import Address, Customer
from customer.models import User as ECUser
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import (Case, F, OuterRef, Prefetch, Q, Subquery, Value,
                              When, Window)
from django.db.models.aggregates import Count, Sum
from django.db.models.functions.window import FirstValue, LastValue
from django.http.response import JsonResponse
from django.utils import timezone
# from finance_api.util import Util
from rest_framework import generics, serializers, status, views, viewsets
from rest_framework.decorators import action, parser_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from TestProject.rest_config import APIResponse, CustomPagination

from sales.models import ActionReport, Invoice, Scheduler
from sales.serializer import (ActionSerializer, InvoiceCreateSerializer,
                              InvoiceSerializer, SchdulerSerializer,
                              SchedulerDetailSerializer, TaskSerializer,
                              UpdateTaskSerializer)


class InvoiceSechdulerView(viewsets.ModelViewSet):
    pass


class CollectionActionView(viewsets.ModelViewSet):
    serializer_class = SchdulerSerializer
    pagination_class = CustomPagination
    def get_queryset(self):
        query = Q()
        status = self.request.GET.get("status")
        is_legal = self.request.GET.get("is_legal")
        customer_id = self.request.GET.get("customer_id")
        # if status:
        #     query.add(Q(status=status),query.connector)
        if customer_id:
            query.add(Q(customer_id=customer_id),query.connector)

        if is_legal == "True":
            query.add(~Q(is_legal=False) & ~Q(status="finished"),query.connector)
        else:
            query.add(~Q(is_legal=True) & ~Q(status="finished"),query.connector)
        # queryset = (SchedulerItem.objects
        #     .filter(query)
        #     .values("id","scheduler_id","customer__name","scheduler__name","scheduler__created_on","total_invoice","customer_id"))
        # # return queryset

        # if status == "pending":
        #     queryset = (SchedulerItem.objects
        #     .filter(status="pending")
        #     .values(
        #         "id",
        #         "scheduler_id",
        #         "customer__name",
        #         "scheduler__name",
        #         "scheduler__created_on",
        #         "total_invoice",
        #         "customer_id"
        #         ))

        #     return queryset

        # elif status == "call_done":
        #     queryset = (SchedulerItem.objects
        #     .select_related("action_scheduler")
        #     .filter(action_scheduler__action_status="done")
        #     .values(
        #         "id",
        #         "scheduler_id",
        #         "customer__name",
        #         "scheduler__name",
        #         "scheduler__created_on",
        #         "total_invoice",
        #         "customer_id",
        #         "action_scheduler__action_date"
        #         ))

        #     return queryset

        # elif status == "call_due":
        #     queryset = (SchedulerItem.objects
        #     .select_related("action_scheduler")
        #     .filter(action_scheduler__action_status="due")
        #     .values(
        #         "id",
        #         "scheduler_id",
        #         "customer__name",
        #         "scheduler__name",
        #         "scheduler__created_on",
        #         "total_invoice",
        #         "customer_id",
        #         "action_scheduler__action_date"
        #         ))

        #     return queryset

        # elif status == "legal_action":
        #     queryset = (SchedulerItem.objects
        #     .select_related("action_scheduler")
        #     .filter(is_legal=True)
        #     .values(
        #         "id",
        #         "scheduler_id",
        #         "customer__name",
        #         "scheduler__name",
        #         "scheduler__created_on",
        #         "total_invoice",
        #         "customer_id",
        #         "action_scheduler__action_date",
        #         "status",
        #         ))
        #     return queryset

        # elif status == "Test":
        #     queryset = (SchedulerItem.objects
        #     .select_related("action_scheduler")
        #     .filter(is_legal=True)
        #     .values(
        #         "id",
        #         "scheduler_id",
        #         "customer__name",
        #         "scheduler__name",
        #         "scheduler__created_on",
        #         "total_invoice",
        #         "customer_id",
        #         "status",
        #         )
        #         .annotate(
        #             legal_status = Case(When(Q(is_legal=True),then=Window(expression=FirstValue("status")))),
        #             action_date = Case(When(~Q(action_scheduler__action_status="finished"),then=Window(expression=FirstValue("action_scheduler__action_date"))))
        #         )
        #         )
        #     return queryset


#     @action(detail=True, methods=['post'])
#     def sent_to_legal_action(self,request,pk=None):
#         # scheduler_id = request.data.get("scheduler_id")
#         SchedulerItem.objects.filter(id=pk).update(is_legal=True)
#         return APIResponse(code=1,message="Reminder has been sent to legal action !")

#     @action(detail=True, methods=['post'])
#     def finish_reminder(self,request,pk=None):
#         # scheduler_id = request.data.get("scheduler_id")
#         SchedulerItem.objects.filter(id=pk).update(status="finished")
#         return APIResponse(code=1,message="scheduler finished")

#     @action(detail=True, methods=['post'])
#     def customer_details(self,request,pk=None):
#         # customer_id = self.request.POST.get("customer_id")
#         object_set = (SchedulerItem.objects
#                         .select_related("scheduler_item")
#                         .filter(id=pk)
#                         .values("customer__name","total_invoice","customer_id")
#                         .annotate(
#                             total_paid_amount = Sum("scheduler_item__invoice__amount_paid"),
#                             total_invoice_amount = Sum("scheduler_item__invoice__invoice_value")
#                         )
#                         .first()
#                         )
#         object_set["total_reminder"] = SchedulerItem.objects.filter(customer_id=object_set["customer_id"]).count()
#         last_reminder_date = SchedulerItem.objects.filter(customer_id=object_set["customer_id"]).values("scheduler__created_on").last()
#         object_set["last_reminder_date"] = last_reminder_date["scheduler__created_on"]
#         address = Address.objects.filter(customer_id=2847).values("email","phone","country__name").first()
#         if address:
#             object_set["email"] = address["email"]
#             object_set["contact"] = address["phone"]
#             object_set["country"] = address["country__name"]
#         serializer = SchedulerDetailSerializer(object_set)
#         return APIResponse(serializer.data)

#     @action(detail=True, methods=["get","list"])
#     def invoice_details(self,request,pk=None):
#         query = Q()
#         if pk is not None:
#             query.add(Q(scheduler_invoice__scheduler_item_id=pk),query.connector)
#         queryset = (Invoice.objects.select_related("scheduler_invoice")
#             .filter(query)
#             .values(
#             "invoice_number",
#             "status__name",
#             "invoice_value",
#             "invoice_created_on",
#             "invoice_due_date",
#             "amount_paid",
#             "scheduler_invoice__scheduler_item__customer__name",
#         ))
#         queryset = queryset = self.filter_queryset(queryset)
#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = InvoiceSerializer(page,many=True)
#             return self.get_paginated_response(serializer.data)

#         serializer = InvoiceSerializer(queryset,many=True)
#         return APIResponse(serializer.data)

# class LegalActionView(viewsets.ModelViewSet):
#     serializer_class = SchdulerSerializer
#     pagination_class = CustomPagination
#     def get_queryset(self):
#         query = Q()
#         status = self.request.GET.get("status")
#         customer_id = self.request.GET.get("customer_id")
#         if status:
#             query.add(Q(status=status),query.connector)
#         elif customer_id:
#             query.add(Q(customer_id=customer_id),query.connector)
#         query.add(~Q(is_legal=False) & ~Q(status="finished"),query.connector)
#         queryset = (SchedulerItem.objects
#             .filter(query)
#             .values("id","scheduler_id","customer__name","scheduler__name","scheduler__created_on","total_invoice"))
#         return queryset

class ActionView(viewsets.ModelViewSet):
    serializer_class = ActionSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        scheduler_id = self.request.GET.get("scheduler_id")
        queryset = ActionReport.objects.filter(scheduler_item_id=scheduler_id).all()
        return queryset

    # def create(self, request):
    #     serializer = self.get_serializer(data=request.data, many=isinstance(request.data,list))
    #     serializer.is_valid(raise_exception=True)
    #     obj = self.perform_create(serializer)
    #     # print(obj,"serializer")
    #     SchedulerItem.objects.filter()
    #     return APIResponse(serializer.data)

    # @action(detail=False, methods=['post'])
    # def delete_action(self,request):
    #     action_ids = request.data.get("ids")
    #     action_ids = [int(id) for id in action_ids.split(",")]
    #     CollectionActionReport.objects.filter(id__in=action_ids).delete()
    #     return APIResponse(code=0, message="Action deleted")

# class CreateSchedulerView(viewsets.ModelViewSet):
#     queryset = SchedulerInvoice.objects.all()
#     serializer_class = CreateSchedulerSerializer
#     pagination_class = CustomPagination

#     def create(self, request):
#         # print(request.data,"scheduler")
#         serializer = self.get_serializer(data=request.data, many=isinstance(request.data,list))
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         return APIResponse(code=1,message="Action created")

# class CollectionActionView(viewsets.ModelViewSet):
#     serializer_class = SchdulerSerializer
#     filterset_class = CollectionActionFilter
#     pagination_class = CustomPagination

#     def get_queryset(self):
#         query = Q()
#         status = self.request.GET.get("status")
#         status = self.request.GET.get("status")
#         print(status,"status")
#         if status:
#             query.add(Q(status__code=status),query.connector)
#         query.add(Q(scheduler_item__isnull=False),query.connector)
#         queryset = (SchedulerItem.objects
#         .prefetch_related("scheduler_item")
#         .filter(query)
#         .values("id","scheduler__name","scheduler__created_on","total_invoice")
#         .annotate())
#         print(queryset,"queryset")
#         return queryset

    # def get_queryset(self):
    #     query = Q()
    #     status = self.request.GET.get("status")
    #     status = self.request.GET.get("status")
    #     print(status,"status")
    #     if status:
    #         query.add(Q(status__code=status),query.connector)
    #     query.add(Q(scheduler_item__isnull=False),query.connector)
    #     queryset = (Scheduler.objects
    #     .prefetch_related("scheduler_item")
    #     .filter(query)
    #     .annotate(
    #         total_invoices = Count("scheduler_item__invoice",distinct=True),
    #         total_reminders = Count("scheduler__id", distinct=True),
    #         customer = F("scheduler_item__customer__company_name"),
    #         # next_action_date =Case(When(~Q(status="pending"),then=F("scheduler__next_action_date")))
    #         # next_action_date = Window(expression=FirstValue("scheduler__next_action_date")),
    #         # legal_status = Case(When(Q(is_legal_action=True),then=F("status")))
    #     )
    #     .exclude(is_legal_action=True)
    #     .distinct())
    #     return queryset

    # @action(detail=True, methods=['post'])
    # def sent_to_legal_action(self,request):
    #     scheduler_id = request.data.get("scheduler_id")
    #     Scheduler.objects.filter(id=scheduler_id).update(is_legal_action=True)
    #     return APIResponse(code=1,message="Reminder has been sent to legal action !")

    # @action(detail=False, methods=['post'])
    # def finish_reminder(self,request):
    #     scheduler_id = request.data.get("scheduler_id")
    #     Scheduler.objects.filter(id=scheduler_id).update(status="finished")
    #     return APIResponse(code=1,message="Reminder deleted")

    # @action(detail=True, methods=['get'])
    # def customer_details(self,request,pk=None):
    #     # scheduler_id = self.request.data.get("scheduler_id")
    #     object_set = (Scheduler.objects
    #         .filter(id=pk)
    #         .prefetch_related("SchedulerItem")
    #         .values("id","scheduler_name","scheduler_item__customer__id","created_on")
    #         .annotate(
    #             total_invoices = Count("scheduler_item__invoice"),
    #             customer = Window(expression=FirstValue("scheduler_item__customer__company_name")),
    #             # total_reminders= Count("scheduler_item__customer__id",distinct=True),
    #             invoices_amount = Sum("scheduler_item__invoice__outstanding_amount"),
    #             total_paid_amount= Sum("scheduler_item__invoice__currency_outstanding_amount"),
    #         )
    #         .first()
    #           )
    #     serializer = SchedulerDetailSerializer(object_set)
        # page = self.paginate_queryset(supplements)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)

        # serializer = self.get_serializer(page, many=True)
        # result_set = serializer.data
        # return APIResponse(serializer.data)

    # @action(detail=True, methods=["get","list"])
    # def invoice_details(self,request,pk=None):
    #     query = Q()
    #     # customer_id = self.request.data.get("customer_id")
    #     # print(pk)
    #     if pk is not None:
    #         # print(pk)
    #         query.add(Q(scheduler_invoice__scheduler_item_id=pk),query.connector)
    #     queryset = (Invoice.objects.select_related("scheduler_invoice")
    #         .filter(query)
    #         .values(
    #         "invoice_number",
    #         "status__name",
    #         "outstanding_amount",
    #         "currency_outstanding_amount",
    #         "invoice_created_on",
    #         "invoice_due_date",
    #         "company__company_name",
    #         "amount_paid",
    #     ))
    #     # print(queryset,"queryset")
    #     queryset = queryset = self.filter_queryset(queryset)
    #     page = self.paginate_queryset(queryset)
    #     # print(page)
    #     if page is not None:
    #         print("page")
    #         serializer = InvoiceSerializer(page,many=True)
    #         return self.get_paginated_response(serializer.data)

    #     serializer = InvoiceSerializer(queryset,many=True)
    #     # data = self.get_paginated_response(serializer.data)
    #     return APIResponse(serializer.data)

    # @action(detail=True, methods=['get',"list"])
    # def reminders(self,request,pk=None):
    #     query = Q()
    #     customer_id = self.request.data.get("customer_id")
    #     if customer_id is not None:
    #         query.add(Q(customer_id=customer_id),query.connector)
    #     query.add(Q(scheduler_item__isnull=False),query.connector)
    #     queryset = (Scheduler.objects
    #     .select_related("SchedulerItem")
    #     .filter(query)
    #     .values(
    #     "id",
    #     "scheduler_name",
    #     "created_on",
    #     "scheduler_item__customer__company_name"
    #     )
    #     .annotate(
    #         total_invoices = Count("scheduler_item__invoice",distinct=True),
    #         total_reminders = Count("scheduler__id",distinct=True)
    #     )
    #     .distinct())
    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         # print("MMMMMMMMMMMMMMM")
    #         serializer = SchdulerSerializer(page,many=True)
    #         # serializer = self.get_serializer(page,many=True)
    #         return self.get_paginated_response(serializer.data)

    #     # serializer = self.get_serializer(page, many=True)
    #     serializer = SchdulerSerializer(queryset,many=True)
    #     return APIResponse(serializer.data)


# class LegalActionView(viewsets.ModelViewSet):
#     serializer_class = SchdulerSerializer
#     pagination_class = CustomPagination
#     # filterset_class = CollectionActionFilter

#     def get_queryset(self):
#         query = Q()
#         customer_id = self.request.data.get("customer_id")
#         status = self.request.data.get("status")
#         if status:
#             query.add(Q(status=status),query.connector)
#         if customer_id:
#             query.add(Q(scheduler_item__invoice__company__id=customer_id),query.connector)
#         else:
#             query.add(Q(is_legal_action=True),query.connector)
#         query.add(Q(scheduler_item__isnull=False),query.connector)
#         queryset = (Scheduler.objects
#         .prefetch_related("scheduler_item")
#         .filter(query)
#         .annotate(
#             total_invoices = Count("scheduler_item__invoice",distinct=True),
#             total_reminders = Count("scheduler__id", distinct=True),
#             customer = Window(expression=FirstValue("scheduler_item__invoice__company__name")),
#             # next_action_dates = Case(When(~Q(status="pending"),then = F("scheduler__next_action_date"))),
#             # next_action_date = Window(expression=FirstValue("scheduler__next_action_date")),
#         )
#         .distinct())
#         return queryset


# class SchedulerDetailView(generics.RetrieveAPIView):
#     serializer_class = SchedulerDetailSerializer
#     def get_object(self):
#         scheduler_id = self.request.data.get("scheduler_id")
#         object_set = (Scheduler.objects
#             .filter(id=scheduler_id)
#             .prefetch_related("SchedulerItem")
#             .values("id","scheduler_name","scheduler_item__customer__id","created_on")
#             .annotate(
#                 total_invoices = Count("scheduler_item__invoice"),
#                 customer = Window(expression=FirstValue("scheduler_item__customer__company_name")),
#                 # total_reminders= Count("scheduler_item__customer__id",distinct=True),
#                 invoices_amount = Sum("scheduler_item__invoice__outstanding_amount"),
#                 total_paid_amount= Sum("scheduler_item__invoice__currency_outstanding_amount"),
#             )
#             .first()
#               )
#         object_set["total_reminders"] = SchedulerItem.objects.filter(customer__id=object_set["scheduler_item__customer__id"]).count()
#         object_set["last_reminder"] = SchedulerItem.objects.filter(customer__id=object_set["scheduler_item__customer__id"]).values("scheduler__created_on").last()["scheduler__created_on"]
#         return object_set

# class InvoiceView(viewsets.ModelViewSet):
#     serializer_class = InvoiceSerializer
#     def get_queryset(self):
#         query = Q()
#         customer_id = self.request.data.get("customer_id")
#         if customer_id is not None:
#             query.add(Q(company_id=customer_id),query.connector)
#         queryset = (Invoice.objects.filter(query).values(
#             "invoice_number",
#             "status__name",
#             "outstanding_amount",
#             "currency_outstanding_amount",
#             "invoice_created_on",
#             "invoice_due_date",
#             "company__company_name",
#             "company__customer_type",

#         ))
#         return queryset

    # @action(detail=True,methods=["get","list"])
    # def customer_invoice(self,request,pk=None):
    #     query = Q()
    #     customer_id = self.request.data.get("customer_id")
    #     if customer_id is not None:
    #         query.add(Q(scheduler_item__schdeluer_id=pk),query.connector)
    #     queryset = (Invoice.objects.select_related("scheduler_item")
    #         .filter(query)
    #         .values(
    #         "invoice_number",
    #         "status__name",
    #         "outstanding_amount",
    #         "currency_outstanding_amount",
    #         "invoice_created_on",
    #         "invoice_due_date",
    #         "company__company_name"
    #     ))
    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         # serializer = InvoiceSerializer(queryset,many=True)
    #         serializer = self.get_serializer(page,many=True)
    #         return APIResponse(serializer.data)

    #     # serializer = self.get_serializer(page, many=True)
    #     serializer = InvoiceSerializer(queryset,many=True)
    #     return APIResponse(serializer.data)

# class CustomerReminder(generics.ListAPIView):
#     serializer_class = SchdulerSerializer
#     pagination_class = CustomPagination
#     def get_queryset(self):
#         query = Q()
#         customer_id = self.request.data.get("customer_id")
#         if customer_id is not None:
#             query.add(Q(scheduler_item__invoice__company__id=customer_id),query.connector)
#         query.add(Q(scheduler_item__isnull=False),query.connector)
#         queryset = (Scheduler.objects
#         .select_related("SchedulerItem")
#         .filter(query)
#         .values(
#         "id",
#         "scheduler_name",
#         "created_on",
#         "scheduler_item__customer__company_name"
#         )
#         .annotate(
#             total_invoices = Count("scheduler_item__invoice",distinct=True),
#             total_reminders = Count("scheduler__id",distinct=True)
#         )
#         .distinct())
#         return queryset

#-----------------collection Action -----------------#


    # @action(detail=True, methods=['post'])
    # def update_action(self,request,pk=None):
    #     action = CollectionAction.objects.get(id=pk)
    #     serializer = self.get_serializer(action, data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     return APIResponse(serializer.data)

# class ActionListView(generics.ListAPIView):
#     serializer_class = ActionSerializer
#     pagination_class = CustomPagination
#     def get_queryset(self):
#         scheduler_id = self.request.data.get("scheduler_id")
#         queryset = (CollectionAction.objects
#         .filter(scheduler_id=scheduler_id)
#         .values("summary","scheduler__scheduler_name","action_by__username","reference","action_date","action_type"))
#         return queryset

# class DeleteActionView(generics.DestroyAPIView):
#     queryset = CollectionAction.objects.filter(is_deleted=False)
#     serializer_class = ActionSerializer

# class UpdateActionView(generics.UpdateAPIView):
#     queryset = CollectionAction.objects.filter(is_deleted=False)
#     serializer_class = ActionSerializer

# class CreateActionView(generics.CreateAPIView):
#     queryset = CollectionAction.objects.all()
#     serializer_class = ActionSerializer
#     def create(self, request):
#         f_action = request.data.get("first_action")
#         next_action = request.data.get("second_action")
#         new_records = []
#         if f_action:
#             f_action = ast.literal_eval(f_action)
#             new_records.append(CollectionAction(
#                 scheduler_id=f_action["scheduler_id"],
#                 action_by_id=f_action["action_by_id"],
#                 action_type=f_action["action_type"],
#                 action_date=f_action["action_date"],
#                 summary=f_action["summary"],
#                 reference=f_action["reference"],
#                 status=f_action["status"]
#             ))
#         if next_action:
#             next_action = ast.literal_eval(next_action)
#             new_records.append(CollectionAction(
#                 scheduler_id=next_action["scheduler_id"],
#                 action_by_id=next_action["action_by_id"],
#                 action_type=next_action["action_type"],
#                 action_date=next_action["action_date"],
#                 summary=next_action["summary"],
#                 reference=next_action["reference"],
#                 status=next_action["status"]
#             ))
#         CollectionAction.objects.bulk_create(new_records)
#         return APIResponse(code=1,message="Action created")


#================== return scheduler data =====================#

# class InvoiceView(viewsets.ModelViewSet):
#     queryset = Invoice.objects.all()
#     serializer_class = InvoiceSerializer

# class SchedulerView(viewsets.ModelViewSet):
#     serializer_class = SchdulerSerializer
#     pagination_class = CustomPagination
#     # filterset_class = SchedulerFilter
#     def get_queryset(self):
#         query = Q()
#         customer_id = self.request.GET.get("customer_id")
#         if customer_id:
#             query.add(Q(customer_id=customer_id),query.connector)
#         queryset = (Scheduler.objects
#             .select_related("scheduler_item")
#             .filter(query)
#             .values("id","scheduler_id","customer__name","scheduler__name","scheduler__created_on","custom er_id")
#             .annotate(
#                 total_invoices = Count("scheduler_item__invoice__id")
#             )
#             )
#         return queryset

#     @action(detail=False, methods=['post'])
#     def send_to_legal_action(self,request):
#         ids = request.data.get("ids")
#         invoice_ids =[]
#         if ids:
#             invoice_ids = [int(x) for x in ids.split(",")]
#         else:
#             return APIResponse(code=0,message="Please select at least one record.")
#         Invoice.objects.filter(id__in=invoice_ids).update(is_legal=True)
#         # attachment_views.insert("sales", "collectionaction", [action["id"]], AuditAction.INSERT, user, c_ip,  "Action "+ action["action_status"].title() +" added.")
#         return APIResponse(code=1,message="Invoice(s) has been sent to legal action.")

#     @action(detail=False, methods=['post'])
#     def customer_details(self,request):
#         customer_id = self.request.POST.get("customer_id")
#         # is_legal = self.request.POST.get("is_legal")
#         query = Q()
#         query.add(Q(id=customer_id),query.connector)
#         address = Address.objects.filter(customer_id=OuterRef('pk')).order_by("-id")[:1]
#         customer = (Customer.objects
#                 .prefetch_related("invoice_customer")
#                 .filter(query)
#                 .values("id","name")
#                 .annotate(
#                             total_invoices = Count("invoice_customer__id"),
#                             total_paid_amount = Sum("invoice_customer__amount_paid"),
#                             total_invoice_amount = Sum("invoice_customer__invoice_value"),
#                             email = Subquery(address.values("email")),
#                             contact = Subquery(address.values("phone")),
#                             country = Subquery(address.values("country__name")),
#                         )
#                 .first())

#         if customer is not None:
#             customer["total_reminder"] = Scheduler.objects.filter(customer_id=customer["id"]).count()
#             last_reminder_date = Scheduler.objects.filter(customer_id=customer["id"]).values("scheduler__created_on").last()
#             customer["last_reminder_date"] = last_reminder_date["scheduler__created_on"]
#         # serializer = CustomerDetailSerializer(customer).data
#         return APIResponse("ok")

#     @action(detail=False, methods=['post'])
#     def finish_invoice(self,request):
#         ids = request.data.get("ids")
#         invoice_ids =[]
#         if ids:
#             invoice_ids =[int(x) for x in ids.split(",")]
#             Invoice.objects.filter(id__in=invoice_ids).update(is_finished=True)
#             return APIResponse(code=1,message="Invoice(s) marked as finished.")
#         else:
#             return APIResponse(code=0,message="Please select at least one record .")

#     @action(detail=False,methods=["post"])
#     def create_scheduler(self,request):
#         data = {
#             "key": "yhlC0v6OTSY0lys9MHmFWkhYyzyaEG09",
#             "funname": "GET_FinAppPaymentReminderScheduleData",
#             "param": {
#                 "SchedualId": 40121
#             }
#         }

#         url = 'http://192.168.1.115:8080/sparrowapp/api/financeapp/'
#         headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
#         response = requests.request("GET",url, data=json.dumps(data), headers=headers)
#         response = response.json()
#         scheduler_list = json.loads(response)
#         scheduler_list = scheduler_list["data"]
#         ec_customer_ids = [x["companyId"] for x in scheduler_list["Customer"]]
#         customer = Customer.objects.filter(ec_customer_id__in=ec_customer_ids).values("id","ec_customer_id")
#         customer_ids = Util.get_dict_from_queryset("ec_customer_id","id",customer)
#         invoice_data = [x["Invoices"] for x in scheduler_list["Customer"]]
#         currency_code = []
#         ec_user_ids = []
#         status_code = []
#         invoices_list = []
#         for invoices in invoice_data:
#             for invoice in invoices:
#                 currency_code.append(invoice["currency"])
#                 ec_user_ids.append("created_by")
#                 invoices_list.append(invoice["invoice_number"])
#                 status_code.append(invoice["status"])
#                 if invoice["secondry_status"]:
#                     status_code.append(invoice["secondry_status"])

#         codes = CodeTable.objects.filter(code__in=status_code).values("id","code")
#         code = Util.get_dict_from_queryset("code","id",codes)

#         #------------------------ Address

#         # address = Address.objects.filter(ec_address_id__in= ec_invoice_iddress).values("id","ec_address_id")
#         # address_ids = Util.get_dict_from_queryset("ec_address_id","id",address)

#         #------------------------ Currency

#         currency = Currency.objects.filter(code__in=currency_code).values("id","code")
#         currency_id = Util.get_dict_from_queryset("code","id",currency)

#         #------------------------ User

#         user = ECUser.objects.filter(customer_id__in = ec_customer_ids).values("id","customer__ec_customer_id")
#         user_ids = Util.get_dict_from_queryset("customer__ec_customer_id","id",user)

#         invoice_create = []
#         invoice_update = []
#         invoice_instances = []
#         exist_invoices = list(Invoice.objects.filter(invoice_number__in=invoices_list).values_list("invoice_number",flat=True))
#         for invoices in invoice_data:
#             for invoice in invoices:
#                 customer_id = customer_ids[invoice["customer"]] if invoice["customer"] in customer_ids else None
#                 invoice["status"] = code[invoice["status"]] if invoice["status"] in code else None
#                 invoice["customer"] = customer_id
#                 invoice["hand_company"] = customer_id
#                 invoice["currency"] = currency_id[invoice["currency"]] if invoice["currency"] in currency_id else None
#                 invoice["created_by"] = user_ids[invoice["created_by"]] if invoice["created_by"] in user_ids else None
#                 invoice["secondry_status"] = code[invoice["secondry_status"]] if invoice["secondry_status"] in code else None
#                 invoice["is_finished"] = False
#                 if invoice["invoice_due_date"] == "":
#                     invoice.pop("invoice_due_date")
#                 if invoice["invoice_close_date"] == "":
#                     invoice.pop("invoice_close_date")
#                 if invoice["last_rem_date"] == "":
#                     invoice.pop("last_rem_date")
#                 if invoice["payment_date"] == "":
#                     invoice.pop("payment_date")
#                 if invoice["invoice_created_on"] == "":
#                     invoice.pop("invoice_created_on")
#                 if invoice["created_on"] == "":
#                     invoice.pop("created_on")

#                 if invoice["invoice_number"] not in exist_invoices:
#                     invoice_create.append(invoice)
#                     print("True")
#                 else:
#                     invoice_update.append(invoice)

#                 # if Invoice.objects.filter(invoice_number=invoice["invoice_number"]).exists():
#                 #     exists = Invoice.objects.get(invoice_number=invoice["invoice_number"])
#                 #     invoice_update.append(invoice)
#                 #     invoice_instances.append(exists)
#                 # else:
#                 #     invoice_create.append(invoice)
#                 # invoice_orders.append(invoice["Orders"])
#         # print(invoice_orders,"invoice_orders")
#         # Invoice.objects.bulk_create(invoice_create)
#         # serializer = InvoiceSerializerC(data=invoice_create, many=isinstance(invoice_create,list))
#         # serializer.is_valid(raise_exception=True)
#         # self.perform_create(serializer)

#         # if invoice_update:
#         #     invoice_instances = Invoice.objects.filter(invoice_number__in=exist_invoices)
#         #     # print("KKKKK",invoice_instances)
#         #     InvoiceSerializerC(invoice_instances, data=invoice_update, partial=False, many=True)
#         #     serializer.is_valid(raise_exception=True)
#         #     # # serializer.save()
#         #     # print("work",invoice_instances)
#         #     self.perform_update(serializer)

#         # scheduler = Scheduler.objects.create(name=scheduler_list["ScheduleName"],created_on=datetime.now())
#         # for sch_d in scheduler_list["Customer"]:
#         #     customer_id = customer_ids[sch_d["companyId"]] if sch_d["companyId"] in customer_ids else None,
#         #     scheduler_items = SchedulerItem.objects.create(scheduler = scheduler,customer_id=customer_id[0])
#         #     scheduler_invoice = SchedulerInvoice.objects.create(scheduler_item_id=scheduler_items.id)
#         #     for invoice in serializer.data:
#         #         if invoice["customer"] == customer_id[0]:
#         #             scheduler_invoice.invoice.add(invoice["id"])
#         #     invoice_ids = []
#         #     for invoice in invoice_instances:
#         #         invoice_ids.append(invoice.id)
#         #         if invoice.customer.id == customer_id[0]:
#         #             scheduler_invoice.invoice.add(invoice.id)
#         #         scheduler_invoice.save()
#         #     CollectionInvoice.objects.filter(invoice__in=invoice_ids).update()
#         return APIResponse(code=1,message="Scheduler created.")

# def validate_ids(data, field="id", unique=True):

#     if isinstance(data, list):
#         id_list = [int(x[field]) for x in data]

#         if unique and len(id_list) != len(set(id_list)):
#             raise ValidationError("Multiple updates to a single {} found".format(field))

#         return id_list

#     return [data]


class SchedulerView(viewsets.ModelViewSet):
    queryset = (Invoice.objects.prefetch_related("scheduler_invoice"))
    serializer_class  = TaskSerializer
    @action(detail=False,methods=["post"])
    def create_scheduler(self,request):
        data = {
            "key": "yhlC0v6OTSY0lys9MHmFWkhYyzyaEG09",
            "funname": "GET_FinAppPaymentReminderScheduleData",
            "param": {
                "SchedualId": 50122
            }
        }

        url = 'http://192.168.1.115:8080/sparrowapp/api/financeapp/'
        headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
        response = requests.request("GET",url, data=json.dumps(data), headers=headers)
        response = response.json()
        scheduler_list = json.loads(response)
        scheduler_list = scheduler_list["data"]
        ec_customer_ids = [x["companyId"] for x in scheduler_list["Customer"]]
        customer = Customer.objects.filter(ec_customer_id__in=ec_customer_ids).values("id","ec_customer_id")
        customer_ids = Util.get_dict_from_queryset("ec_customer_id","id",customer)
        invoice_data = [x["Invoices"] for x in scheduler_list["Customer"]]
        currency_code = []
        ec_user_ids = []
        status_code = []
        invoices_list = []
        for invoices in invoice_data:
            for invoice in invoices:
                currency_code.append(invoice["currency"])
                ec_user_ids.append("created_by")
                invoices_list.append(invoice["invoice_number"])
                status_code.append(invoice["status"])
                if invoice["secondry_status"]:
                    status_code.append(invoice["secondry_status"])

        codes = CodeTable.objects.filter(code__in=status_code).values("id","code")
        code = Util.get_dict_from_queryset("code","id",codes)

        #------------------------ Address

        # address = Address.objects.filter(ec_address_id__in= ec_invoice_iddress).values("id","ec_address_id")
        # address_ids = Util.get_dict_from_queryset("ec_address_id","id",address)

        #------------------------ Currency

        currency = Currency.objects.filter(code__in=currency_code).values("id","code")
        currency_id = Util.get_dict_from_queryset("code","id",currency)

        #------------------------ User

        user = ECUser.objects.filter(customer_id__in = ec_customer_ids).values("id","customer__ec_customer_id")
        user_ids = Util.get_dict_from_queryset("customer__ec_customer_id","id",user)

        invoice_create = []
        invoice_update = []
        invoices_instance = Invoice.objects.filter(invoice_number__in=invoices_list)
        exist_invoices = list(invoices_instance.values_list("invoice_number",flat=True))
        for invoices in invoice_data:
            for invoice in invoices:
                customer_id = customer_ids[invoice["customer"]] if invoice["customer"] in customer_ids else None
                invoice["status"] = code[invoice["status"]] if invoice["status"] in code else None
                invoice["customer"] = customer_id
                invoice["hand_company"] = customer_id
                invoice["currency"] = currency_id[invoice["currency"]] if invoice["currency"] in currency_id else None
                invoice["created_by"] = user_ids[invoice["created_by"]] if invoice["created_by"] in user_ids else None
                invoice["secondry_status"] = code[invoice["secondry_status"]] if invoice["secondry_status"] in code else None
                invoice["is_finished"] = False
                if invoice["invoice_due_date"] == "":
                    invoice.pop("invoice_due_date")
                if invoice["invoice_close_date"] == "":
                    invoice.pop("invoice_close_date")
                if invoice["last_rem_date"] == "":
                    invoice.pop("last_rem_date")
                if invoice["payment_date"] == "":
                    invoice.pop("payment_date")
                if invoice["invoice_created_on"] == "":
                    invoice.pop("invoice_created_on")
                if invoice["created_on"] == "":
                    invoice.pop("created_on")

                if invoice["invoice_number"] not in exist_invoices:
                    invoice_create.append(invoice)
                else:
                    invoice_update.append(invoice)
        serializer = self.get_serializer(data=invoice_create,many=True)
        serializer.is_valid(raise_exception=True)
        serializer = self.perform_create(serializer)
        if invoices_instance:
            serializer = UpdateTaskSerializer(instance=invoices_instance,data=invoice_update,many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

        invoices_ = Invoice.objects.filter(invoice_number__in=invoices_list).values("id","customer")
        for sch_d in scheduler_list["Customer"]:
            customer_id = customer_ids[sch_d["companyId"]] if sch_d["companyId"] in customer_ids else None,
            scheduler = Scheduler.objects.create(name = scheduler_list["ScheduleName"],customer_id=customer_id[0])

            if invoices_instance:
                for invoice in invoices_instance:
                    if invoice.customer is not None and  invoice.customer.id == customer_id[0]:
                        scheduler.invoice.add(invoice.id)
            else:
                for invoice in invoices_:
                    if invoice["customer"] == customer_id[0] and invoice["customer"] is not None:
                        scheduler.invoice.add(invoice["id"])

        return APIResponse(code=1,message="scheduler created")


class CollectionInvoiceView(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    pagination_class = CustomPagination



    # filterset_class = InvoiceFilter
    # ordering=[F('action_date').asc(nulls_last=True)]
    def get_queryset(self):
        query = Q()
        customer_id = self.request.GET.get("customer_id")
        status = self.request.GET.get("status")
        if status in ["due","done"]:
            print("due Done")
            query.add(Q(actionreport_invoice__action_status=status),query.connector)
            query.add(Q(is_finished=False),query.connector)
        elif status == "finished":
            query.add(Q(is_finished=True),query.connector)
        address = Address.objects.filter(customer_id=OuterRef('customer_id')).order_by("-id")[:1]
        actions = ActionReport.objects.filter(customer_id=OuterRef('customer_id')).order_by("-id")[:1]
        # print("AALLLLLLLLL")
        queryset = (Invoice.objects
            .prefetch_related("scheduler_invoice")
            .filter(query)
            .values("id","invoice_number","is_finished","payment_tracking_number","customer_id","invoice_created_on","amount_paid","last_rem_date","is_legal")
            .annotate(
                    status = F("status__desc"),
                    customer_name = F("customer__name"),
                    # total_reminder = Count("scheduler_invoice__scheduler_item__id",distinct=True),
                    country = Subquery(address.values("country__name")),
                    # action_status =Case(
                    #     # When(~Q(is_legal=True) & ~Q(is_finished=True),then=F("collectioninvoice_invoice__action__action_status")),
                    #     ),
                    action_date =  Subquery(actions.values("action_date")),
                    action_id =  Subquery(actions.values("id")),
                    invoice_amount = F("invoice_value"),
                )
            .order_by("-action_id")
            .distinct())
        return queryset
