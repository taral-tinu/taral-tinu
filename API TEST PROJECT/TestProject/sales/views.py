import ast
import logging
import re
from itertools import chain
from posixpath import split

from base.models import *
from customer.models import *
from customer.models import Address, Customer
from django.contrib.auth.models import User
from django.db.models import (Case, F, Prefetch, Q, Subquery, Value, When,
                              Window)
from django.db.models.aggregates import Count, Sum
from django.db.models.functions.window import FirstValue, LastValue
from django.http.response import JsonResponse
from django.utils import timezone
# from finance_api.finance_api import util
from finance_api.rest_config import APIResponse, CustomPagination
from finance_api.util import Util
from rest_framework import generics, serializers, status, views, viewsets
from rest_framework.decorators import action, parser_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from sales.models import (CollectionAction, Invoice, Scheduler,
                          SchedulerInvoice, SchedulerItem)
from sales.serializers import (ActionSerializer, CreateSchedulerSerializer,
                               InvoiceSerializer, SchdulerSerializer,
                               SchedulerDetailSerializer)


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
        queryset = (SchedulerItem.objects
            .filter(query)
            .values("id","scheduler_id","customer__name","scheduler__name","scheduler__created_on","total_invoice","customer_id"))
        # return queryset

        if status == "pending":
            queryset = (SchedulerItem.objects
            .filter(status="pending")
            .values(
                "id",
                "scheduler_id",
                "customer__name",
                "scheduler__name",
                "scheduler__created_on",
                "total_invoice",
                "customer_id"
                ))

            return queryset

        elif status == "call_done":
            queryset = (SchedulerItem.objects
            .select_related("action_scheduler")
            .filter(action_scheduler__action_status="done")
            .values(
                "id",
                "scheduler_id",
                "customer__name",
                "scheduler__name",
                "scheduler__created_on",
                "total_invoice",
                "customer_id",
                "action_scheduler__action_date"
                ))

            return queryset

        elif status == "call_due":
            queryset = (SchedulerItem.objects
            .select_related("action_scheduler")
            .filter(action_scheduler__action_status="due")
            .values(
                "id",
                "scheduler_id",
                "customer__name",
                "scheduler__name",
                "scheduler__created_on",
                "total_invoice",
                "customer_id",
                "action_scheduler__action_date"
                ))

            return queryset

        elif status == "legal_action":
            queryset = (SchedulerItem.objects
            .select_related("action_scheduler")
            .filter(is_legal=True)
            .values(
                "id",
                "scheduler_id",
                "customer__name",
                "scheduler__name",
                "scheduler__created_on",
                "total_invoice",
                "customer_id",
                "action_scheduler__action_date",
                "status",
                ))
            return queryset

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


    @action(detail=True, methods=['post'])
    def sent_to_legal_action(self,request,pk=None):
        # scheduler_id = request.data.get("scheduler_id")
        SchedulerItem.objects.filter(id=pk).update(is_legal=True)
        return APIResponse(code=1,message="Reminder has been sent to legal action !")

    @action(detail=True, methods=['post'])
    def finish_reminder(self,request,pk=None):
        # scheduler_id = request.data.get("scheduler_id")
        SchedulerItem.objects.filter(id=pk).update(status="finished")
        return APIResponse(code=1,message="scheduler finished")

    @action(detail=True, methods=['post'])
    def customer_details(self,request,pk=None):
        # customer_id = self.request.POST.get("customer_id")
        object_set = (SchedulerItem.objects
                        .select_related("scheduler_item")
                        .filter(id=pk)
                        .values("customer__name","total_invoice","customer_id")
                        .annotate(
                            total_paid_amount = Sum("scheduler_item__invoice__amount_paid"),
                            total_invoice_amount = Sum("scheduler_item__invoice__invoice_value")
                        )
                        .first()
                        )
        object_set["total_reminder"] = SchedulerItem.objects.filter(customer_id=object_set["customer_id"]).count()
        last_reminder_date = SchedulerItem.objects.filter(customer_id=object_set["customer_id"]).values("scheduler__created_on").last()
        object_set["last_reminder_date"] = last_reminder_date["scheduler__created_on"]
        address = Address.objects.filter(customer_id=2847).values("email","phone","country__name").first()
        if address:
            object_set["email"] = address["email"]
            object_set["contact"] = address["phone"]
            object_set["country"] = address["country__name"]
        serializer = SchedulerDetailSerializer(object_set)
        return APIResponse(serializer.data)

    @action(detail=True, methods=["get","list"])
    def invoice_details(self,request,pk=None):
        query = Q()
        if pk is not None:
            query.add(Q(scheduler_invoice__scheduler_item_id=pk),query.connector)
        queryset = (Invoice.objects.select_related("scheduler_invoice")
            .filter(query)
            .values(
            "invoice_number",
            "status__name",
            "invoice_value",
            "invoice_created_on",
            "invoice_due_date",
            "amount_paid",
            "scheduler_invoice__scheduler_item__customer__name",
        ))
        queryset = queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = InvoiceSerializer(page,many=True)
            return self.get_paginated_response(serializer.data)

        serializer = InvoiceSerializer(queryset,many=True)
        return APIResponse(serializer.data)

class LegalActionView(viewsets.ModelViewSet):
    serializer_class = SchdulerSerializer
    pagination_class = CustomPagination
    def get_queryset(self):
        query = Q()
        status = self.request.GET.get("status")
        customer_id = self.request.GET.get("customer_id")
        if status:
            query.add(Q(status=status),query.connector)
        elif customer_id:
            query.add(Q(customer_id=customer_id),query.connector)
        query.add(~Q(is_legal=False) & ~Q(status="finished"),query.connector)
        queryset = (SchedulerItem.objects
            .filter(query)
            .values("id","scheduler_id","customer__name","scheduler__name","scheduler__created_on","total_invoice"))
        return queryset

class ActionView(viewsets.ModelViewSet):
    serializer_class = ActionSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        scheduler_id = self.request.GET.get("scheduler_id")
        queryset = CollectionAction.objects.filter(scheduler_item_id=scheduler_id).all()
        return queryset

    def create(self, request):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data,list))
        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)
        # print(obj,"serializer")
        SchedulerItem.objects.filter()
        return APIResponse(serializer.data)

    @action(detail=False, methods=['post'])
    def delete_action(self,request):
        action_ids = request.data.get("ids")
        action_ids = [int(id) for id in action_ids.split(",")]
        CollectionAction.objects.filter(id__in=action_ids).delete()
        return APIResponse(code=0, message="Action deleted")

class CreateSchedulerView(viewsets.ModelViewSet):
    queryset = SchedulerInvoice.objects.all()
    serializer_class = CreateSchedulerSerializer
    pagination_class = CustomPagination

    def create(self, request):
        # print(request.data,"scheduler")
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data,list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(code=1,message="Action created")

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
