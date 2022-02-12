import datetime
import json
import logging
import mimetypes
import os
import re
import urllib
import urllib.parse
from datetime import date

import pdfkit
from accounts.models import UserProfile
from auditlog import views as log_views
from auditlog.models import AuditAction
# from azure.storage.blob import BlobClient
from base import views as base_views
from base.models import AppResponse, BaseAttachmentTag
from base.util import Util
from crm.models import Deal
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.db import connection
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from eda.models import Part
from elasticsearch import Elasticsearch
from exception_log import manager
from products.models import Product
from sparrow.decorators import check_view_permission
from stronghold.decorators import public

from attachment.document_service import Attachment as Document
from attachment.models import FileType, Tag

from .models import Attachment

# from uuid import uuid4





es = ""
if settings.ELASTIC_URL:
    es = Elasticsearch([settings.ELASTIC_URL], timeout=30)


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def delete_attachment(request):
    try:
        app_name = request.POST["app"]
        model_name = request.POST["model"]
        user_id = request.user.id
        user = User.objects.get(id=user_id)

        if Util.has_perm("can_delete_attachment", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")

        c_ip = get_client_ip(request)
        u_id = request.session["userid"]
        model = apps.get_model(app_name, model_name)

        if request.POST.get("doc_uid") is not None:
            doc_uid = request.POST.get("doc_uid")
            attachment = model.objects.filter(uid=doc_uid).first()
        else:
            id = int(request.POST["id"])
            attachment = model.objects.filter(id=id).first()

        attachment.deleted = True
        attachment.is_public = False
        attachment.save()

        tag_model_name = model_name
        tag_model_name = tag_model_name.replace("_", "")
        tag_model_name = tag_model_name + "Tag"

        model_exist = False
        try:
            apps.get_model(app_name, tag_model_name)
            model_exist = True
        except LookupError:
            model_exist = False

        if model_exist:
            tag_model = apps.get_model(app_name, tag_model_name)
            doc_tag = tag_model.objects.filter(attachment_id=attachment.id)
            doc_tag.delete()

        es_attachment = Document()
        es_attachment.delete_attachment(attachment.id, model_name=model_name)
        # container_name = settings.AZURE_BLOB["container_name"]
        # conn_str = settings.AZURE_BLOB["conn_str"]
        # blob = BlobClient.from_connection_string(conn_str=conn_str, container_name=container_name, blob_name=str(attachment.url).split("/")[-1])
        # exists = blob.exists()
        # if exists:
        #     blob.delete_blob()
        # elif os.path.exists(str(settings.MEDIA_ROOT) + str(attachment.url)):
        #     os.remove(settings.MEDIA_ROOT + str(attachment.url))
        os.remove(settings.MEDIA_ROOT + str(attachment.url))
        log_views.insert(app_name, model_name, [attachment.id], AuditAction.INSERT, u_id, c_ip, attachment.name + " deleted.")
        object_id = attachment.object_id if attachment.object_id else 0
        return HttpResponse(json.dumps({"code": 1, "msg": "Data removed.", "object_id": object_id, "id": attachment.id}), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def dialog_template(request):
    file_types = FileType.objects.filter(is_active=True)
    return render(request, "attachment/dialog.html", {"file_types": file_types})


"""
download: Responds with download stream, todo: This needs improvement, may not work.
"""


@csrf_exempt
@public
def download_attachment(request):
    app_name = request.GET["app"] if request.GET.get("a") is None else request.GET.get("a")
    model_name = request.GET["model"] if request.GET.get("m") is None else request.GET.get("m")
    uid = request.GET["uid"]
    user_id = request.user.id if request.user else None
    return download_attachment_uid(app_name, model_name, uid, user_id)


def download_attachment_uid(app_name, model_name, uid, user_id):
    try:
        model = apps.get_model(app_name, model_name)
        attachment = model.objects.filter(uid=uid).first()
        file_name = attachment.name
        if attachment.file_type_id is None:
            # if model_name == "part_attachment":
            #     conn_str = settings.AZURE_BLOB["conn_str"]
            #     container_name = settings.AZURE_BLOB["container_name"]
            #     public_url = settings.AZURE_BLOB["public_url"]
            #     file_path = f"{public_url}{container_name}/{str(attachment.url)}"
            #     contenttype = mimetypes.guess_type(file_path)[0]
            #     blob = BlobClient.from_connection_string(conn_str=conn_str, container_name=container_name, blob_name=str(attachment.url).split("/")[-1])
            #     if blob.exists():
            #         download_stream = blob.download_blob()
            #         properties = blob.get_blob_properties()
            #         response = HttpResponse(download_stream.readall())
            #         response["Content-Length"] = str(properties["size"])
            #         response["Content-Disposition"] = 'attachment; filename="' + file_name + '"'
            #     elif os.path.exists(str(settings.MEDIA_ROOT) + str(attachment.url)):
            #         file_path = str(settings.MEDIA_ROOT) + str(attachment.url)
            #         contenttype = mimetypes.guess_type(file_path)[0]
            #         fp = open(file_path, "rb")
            #         response = HttpResponse(fp.read())
            #         fp.close()
            #         response["Content-Length"] = os.path.getsize(file_path)
            #     else:
            #         return HttpResponse("File not Found.")
            # else:
            file_path = str(settings.MEDIA_ROOT) + str(attachment.url)
            contenttype = mimetypes.guess_type(file_path)[0]
            if "s3.amazonaws.com" in settings.MEDIA_ROOT:
                key = default_storage.bucket.lookup(str(attachment.url))
                response = HttpResponse(key)
                response["Content-Length"] = key.size
            else:
                fp = open(file_path, "rb")
                response = HttpResponse(fp.read())
                fp.close()
                response["Content-Length"] = os.path.getsize(file_path)

            response["Content-Type"] = contenttype

            if contenttype is not None and contenttype.split("/")[-1] in ["pdf", "png", "jpg", "jpeg", "bmp", "gif"]:
                response["Content-Disposition"] = "inline;filename=%s" % urllib.parse.quote(file_name)
            else:
                response["Content-Disposition"] = "attachment; filename=%s" % urllib.parse.quote(file_name)
        else:
            config = pdfkit.configuration(wkhtmltopdf=str(settings.WKTHTML_PDF_PATH))
            options = {"page-size": "A4", "margin-top": "0.2in", "margin-right": "0.3in", "margin-bottom": "0.2in", "margin-left": "0.2in", "encoding": "UTF-8", "no-outline": None}
            data = pdfkit.from_url(file_path, False, configuration=config, options=options)
            response = HttpResponse(data, content_type="application/pdf")
            response["Content-Disposition"] = "inline;filename=%s" % urllib.parse.quote(file_name)

        if user_id is not None:
            return response
        if user_id is None:
            if attachment.is_public is True:
                return response
            else:
                return HttpResponse("You don't have permission to access this document.")
    except Exception as e:
        logging.exception(e)
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def get_attachments(request):
    try:

        object_id = request.POST.get("object_id")
        search_type = request.POST.get("search_type")
        app = request.POST.get("app")
        model = request.POST.get("model")

        if search_type == "doc":
            search_data = request.POST.get("search_filter")
        else:
            search_data = request.POST.get("search_filter")
            if len(search_data) > 2:
                search_data = search_data.strip("][")
                search_data = [int(x) for x in search_data.split(",")]
            else:
                search_data = ""
        es_attachment = Document()
        page_index = request.POST.get("page_index") if request.POST.get("page_index") is not None else 1
        results = es_attachment.get_attachments(int(page_index) - 1, 25, search_data, object_id, search_type, app, model)
        documents = results["hits"]["hits"]
        recordsTotal = results["hits"]["total"]["value"]
        response = {"data": [], "total_attachments": recordsTotal, "count": len(documents)}

        product_ids = []
        part_ids = []
        deal_ids = []
        user_ids = []
        for document in documents:
            user_ids.append(document["_source"]["user_id"])
            if document["_source"]["app_name"] == "part":
                part_ids.append(document["_source"]["entity_id"])
            if document["_source"]["app_name"] == "products":
                product_ids.append(document["_source"]["entity_id"])
            if document["_source"]["app_name"] == "crm":
                deal_ids.append(document["_source"]["entity_id"])

        user_data = {}
        users = UserProfile.objects.filter(is_deleted=False, user_id__in=user_ids).values("user_id", "profile_image", "user__first_name", "user__last_name")

        for user in users:
            user_data[user["user_id"]] = [{"first_name": user["user__first_name"], "last_name": user["user__last_name"], "profile_image": user["profile_image"]}]

        products_data = {}
        products = Product.objects.filter(id__in=product_ids).values("id", "name")

        for product in products:
            products_data[product["id"]] = product["name"]

        parts_data = {}
        parts = Part.objects.filter(id__in=part_ids).values("id", "name")

        for part in parts:
            parts_data[part["id"]] = part["name"]
        deal_data = {}
        deals = Deal.objects.filter(id__in=deal_ids).values("id", "description")
        for deal in deals:
            deal_data[deal["id"]] = deal["description"]
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        perms = ["can_add_update", "can_upload_document", "can_delete_attachment", "can_make_attachment_public"]
        permissions = Util.get_permission_role(user, perms)
        selected_tag_id = []

        for document in documents:
            if "tags" in document["_source"] and len(document["_source"]["tags"]) > 0:
                for tag in document["_source"]["tags"]:
                    selected_tag_id.append(tag["id"])

        all_tags = {}
        tags = Tag.objects.filter(id__in=selected_tag_id)
        for tag in tags:
            tag_name = get_hierarchy_tag(tag, tag.name)
            all_tags[tag.id] = tag_name
        for document in documents:
            source_doc = document["_source"]["source_doc"] if "source_doc" in document["_source"] else ""

            if document["_source"]["app_name"] == "products":
                source_doc = products_data[document["_source"]["entity_id"]]

            if document["_source"]["app_name"] == "part":
                source_doc = parts_data[document["_source"]["entity_id"]]
            if document["_source"]["app_name"] == "crm":
                if document["_source"]["entity_id"] in deal_data:
                    source_doc = deal_data[document["_source"]["entity_id"]]

            first_name = user_data[document["_source"]["user_id"]][0]["first_name"]
            last_name = user_data[document["_source"]["user_id"]][0]["last_name"]
            user_pic = Util.get_resource_url("profile", (user_data[document["_source"]["user_id"]][0]["profile_image"]))

            file_type_id = None
            if "file_type_id" in document["_source"].keys():
                file_type_id = document["_source"]["file_type_id"]

            attachment_id = ""
            if "attachment_id" not in document["_source"]:
                attachment_id = document["_id"]
            else:
                attachment_id = document["_source"]["attachment_id"]

            app_name = document["_source"]["app_name"]
            model_name = document["_source"]["model_name"]
            model_name = model_name.replace("_", "")
            model_name = model_name + "Tag"

            model_exist = False
            try:
                apps.get_model(app_name, model_name)
                model_exist = True
            except LookupError:
                model_exist = False
            create_date = None
            try:
                if document["_source"]["created_on"].split("+")[1]:
                    pass
            except IndexError:
                document["_source"]["created_on"] = document["_source"]["created_on"] + "+00:00"
            try:
                create_date = datetime.datetime.strptime(document["_source"]["created_on"], "%d/%m/%Y").strftime("%Y-%m-%d")
            except ValueError:
                create_date = datetime.datetime.strptime(document["_source"]["created_on"], "%Y-%m-%dT%H:%M:%S.%f+00:00").strftime("%Y-%m-%d")

            selected_tags = []

            if model_exist:
                if "tags" in document["_source"]:
                    for tag in document["_source"]["tags"]:
                        if tag["id"] in all_tags:
                            selected_tags.append({"id": tag["id"], "name": all_tags[tag["id"]]})
            response["data"].append(
                {
                    "id": attachment_id,
                    "object_id": document["_source"]["entity_id"],
                    "name": document["_source"]["name"],
                    "user": first_name + " " + last_name,
                    "create_date": create_date,
                    "size": str(round(document["_source"]["size"], 2)) + " KB",
                    "app_name": document["_source"]["app_name"],
                    "model_name": document["_source"]["model_name"],
                    "source_doc": source_doc,
                    "user_pic": user_pic,
                    "uid": document["_source"]["uid"],
                    "title": document["_source"]["title"] if "title" in document["_source"] else "",
                    "subject": document["_source"]["subject"] if "subject" in document["_source"] else "",
                    "description": document["_source"]["description"] if "description" in document["_source"] else "",
                    "isSelected": False,
                    "file_type_id": file_type_id,
                    "permissions": json.dumps(permissions),
                    "model_exist": model_exist,
                    "selected_tags": selected_tags,
                    "is_public": document["_source"]["is_public"] if "is_public" in document["_source"] else "",
                }
            )
        return HttpResponse(AppResponse.get(response), content_type="json")

    except Exception as e:
        logging.exception(e)
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def get_attchment_object(attachment):
    user = attachment.user
    user_name = user.first_name + " " + user.last_name
    user_id = user.id
    users = UserProfile.objects.filter(user_id=user_id).values("user_id", "profile_image")
    imageurl = {}
    for user in users:
        imageurl[user["user_id"]] = user["profile_image"]
    img_src = Util.get_resource_url("profile", str(imageurl[attachment.user_id])) if attachment.user_id in imageurl and imageurl[attachment.user_id] else ""
    file_type = ""
    if attachment.file_type is not None:
        file_type = attachment.file_type.description
    return {
        "attachment_id": attachment.id,
        "uid": attachment.uid,
        "name": attachment.name,
        "size": str(round(attachment.size, 2)) + " KB",
        "url": str(attachment.url),
        "user": user_name,
        "source_doc": attachment.source_doc,
        "user_id": user_id,
        "entity_id": attachment.object_id,
        "create_date": Util.get_local_time(attachment.create_date),
        "file_type": file_type,
        "is_public": attachment.is_public,
        "created_on": Util.get_local_time(attachment.create_date),
        "title": attachment.title,
        "subject": attachment.subject,
        "img_src": img_src,
        "isSelected": False,
        "description": attachment.description,
        "workcenter_id": attachment.workcenter_id if hasattr(attachment, "workcenter_id") and attachment.workcenter_id else 0,
        "workcenter_name": attachment.workcenter.name if hasattr(attachment, "workcenter_id") and attachment.workcenter_id else "",
    }


def upload_attachment(request):
    response = {"data": []}
    try:
        app_name = request.POST["app"]
        model_name = request.POST["model"]
        file_type_id = request.POST.get("file_type")
        object_id = int(request.POST["object_id"])
        c_ip = get_client_ip(request)
        if "userid" in request.session:
            u_id = request.session["userid"]
        else:
            u_id = request.user.id
        file_name = request.FILES["file"]
        public = request.POST.get("makePublic")
        source_doc = request.POST.get("source_doc") if request.POST.get("source_doc") is not None else ""
        is_public = False
        if public == "true":
            is_public = True
        user = User.objects.get(id=u_id)

        if Util.has_perm("can_make_attachment_public", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")

        is_not_valid = (
            str(file_name)
            .lower()
            .endswith(
                (
                    ".bat",
                    ".exe",
                    ".cmd",
                    ".sh",
                    ".p",
                    ".cgi",
                    ".386",
                    ".dll",
                    ".com",
                    ".torrent",
                    ".js",
                    ".app",
                    ".jar",
                    ".pif",
                    ".vb",
                    ".vbscript",
                    ".wsf",
                    ".asp",
                    ".cer",
                    ".csr",
                    ".jsp",
                    ".drv",
                    ".sys",
                    ".ade",
                    ".adp",
                    ".bas",
                    ".chm",
                    ".cpl",
                    ".crt",
                    ".csh",
                    ".fxp",
                    ".hlp",
                    ".hta",
                    ".inf",
                    ".ins",
                    ".isp",
                    ".jse",
                    ".htaccess",
                    ".htpasswd",
                    ".ksh",
                    ".lnk",
                    ".mdb",
                    ".mde",
                    ".mdt",
                    ".mdw",
                    ".msc",
                    ".msi",
                    ".msp",
                    ".mst",
                    ".ops",
                    ".pcd",
                    ".prg",
                    ".reg",
                    ".scr",
                    ".sct",
                    ".shb",
                    ".shs",
                    ".url",
                    ".vbe",
                    ".vbs",
                    ".wsc",
                    ".wsf",
                    ".wsh",
                    ".php",
                    ".php1",
                    ".php2",
                    ".php3",
                    ".php4",
                    ".php5",
                )
            )
        )
        if is_not_valid:
            return HttpResponse(AppResponse.msg(0, "This file type is not allowed to upload."), content_type="json")

        # For uploading on AZURE_CLOUD.

        # is_cloud = request.POST.get("is_cloud")
        # if is_cloud == "true":
        #     is_cloud = True
        # else:
        #     is_cloud = False

        # is_cloud = False
        # attachment = upload(is_cloud, app_name, model_name, object_id, request.FILES["file"], file_type_id, c_ip, "-", u_id, is_public, source_doc)

        attachment = upload(app_name, model_name, object_id, request.FILES["file"], file_type_id, c_ip, "-", u_id, is_public, source_doc)

        response["code"] = 1
        response["data"] = [get_attchment_object(attachment)]
        response["msg"] = "File uploaded."

    except Exception as e:
        response["code"] = 0
        response["msg"] = str(e)
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")
    return HttpResponse(AppResponse.get(response), content_type="json")


def attachment_change_access(request):
    try:
        app_name = request.POST["app"]
        model_name = request.POST["model"]
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        permission = Util.has_perm("can_make_attachment_public", user)
        if permission is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
        attachment_id = int(request.POST["id"])
        model = apps.get_model(app_name, model_name)

        attachment = model.objects.filter(id=int(attachment_id)).first()
        if attachment.is_public is True:
            attachment.is_public = False
        else:
            attachment.is_public = True
        attachment.save()
        response = {"data": []}
        response["access"] = attachment.is_public
        response["id"] = attachment.id
        response["permission"] = permission
        return HttpResponse(AppResponse.get(response), content_type="json")

    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def upload_and_save_attachment(data, app_name, model_name, object_id, u_id, c_ip, code, file_name):
    try:
        # domain = request.META['HTTP_HOST']
        file_type = FileType.objects.filter(code=code, is_active=True).first()
        rootFolderName = app_name + "/" + model_name.replace("_attachment", "").lower()
        file_rootpath = Attachment.get_file_rootpath(rootFolderName)
        file_path = os.path.join(file_rootpath, file_name)
        full_path = str(settings.MEDIA_ROOT) + file_path
        data_new = full_path.rsplit("/", 1)
        if len(data_new) > 0 and data_new[0] != "":
            parent_dir = str(data_new[0])
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
        if not os.path.isfile(full_path):
            with open(full_path, "wb") as f:
                f.write(data)
            size = os.path.getsize(full_path) / 1024
            # upload(False, app_name, model_name, object_id, file_path, file_type.id, c_ip, "-", u_id, False, "", file_name, size)
            upload(app_name, model_name, object_id, file_path, file_type.id, c_ip, "-", u_id, False, "", file_name, size)

        return full_path
    except Exception as e:
        manager.create_from_exception(e)
        return ""


# def upload(_is_cloud, _app_name, _model_name, _object_id, _docfile, _file_type, _ip_addr, _checksum, _user_id, is_public, source_doc, _name=None, _size=None, doc_type="gen"):
def upload(_app_name, _model_name, _object_id, _docfile, _file_type, _ip_addr, _checksum, _user_id, is_public, source_doc, _name=None, _size=None, doc_type="gen"):

    try:
        if _name is None:
            _name = _docfile._name

        if _size is None:
            _size = _docfile.size / 1024

        model = apps.get_model(_app_name, _model_name)
        file_type_ref = None
        if _file_type is not None and _file_type != "" and _file_type != "null":
            file_type_ref = int(_file_type)

        attachment = model(
            name=_name,
            object_id=_object_id,
            size=_size,
            ip_addr=_ip_addr,
            checksum=_checksum,
            user_id=_user_id,
            doc_type=doc_type,
            file_type_id=file_type_ref,
            is_public=is_public,
            source_doc=source_doc,
        )

        attachment.save()
        _is_cloud = False
        if _is_cloud:
            pass
            # For uploading content to AZURE_CLOUD
            # conn_str = settings.AZURE_BLOB["conn_str"]
            # cloud_domain = settings.AZURE_BLOB["public_url"]
            # container_name = settings.AZURE_BLOB["container_name"]

            # Create file name
            # _uid = str(uuid4())
            # file_name = _uid + "_" + _name

            # # Upload file to cloud
            # blob = BlobClient.from_connection_string(conn_str=conn_str, container_name=container_name, blob_name=file_name)
            # file_data = _docfile.file.getvalue()
            # blob.upload_blob(file_data)

            # # Regular path
            # # _url = f"eda/eda/part/{str(datetime.date.today().year)}/{str(datetime.date.today().month)}/{str(datetime.date.today().day)}/{file_name}"

            # _cloud_url = f"{cloud_domain}{container_name}/{file_name}"
            # # save url to model (Part Attachment)
            # attachment.uid = str(_uid)
            # attachment.url = str(_cloud_url)
        else:
            attachment.url = _docfile

        attachment.save()
        # Indext attachment in ES
        Document().insert([attachment], app_name=_app_name, model_name=_model_name)

        log_views.insert(_app_name, _model_name, [attachment.id], AuditAction.INSERT, _user_id, _ip_addr, _name + " uploaded.")

        return attachment
    except Exception as e:
        logging.exception(e)
        manager.create_from_exception(e)
        return None
        # return HttpResponse(AppResponse.msg(0, str(e)), content_type = 'json')


def attachment_properties(request):
    try:
        # attachment_es_update = {}
        field_name = request.POST.get("field_name")
        app_name = request.POST.get("app")
        model_name = request.POST.get("model")

        value = request.POST.get("value")
        attachment_id = request.POST["attachment_id"]
        object_id = int(request.POST["object_id"])
        attachment = apps.get_model(app_name, model_name)
        attachment_saves = attachment.objects.filter(id=attachment_id).first()
        es_attachment = Document()

        if str(field_name) == "title":
            attachment_saves.title = value
            es_attachment.update_attachment(attachment_id=attachment_id, title=value, app_name=app_name, model_name=model_name)

        if str(field_name) == "subject":
            attachment_saves.subject = value
            es_attachment.update_attachment(attachment_id=attachment_id, subject=value, app_name=app_name, model_name=model_name)

        if str(field_name) == "description":
            attachment_saves.description = value
            es_attachment.update_attachment(attachment_id=attachment_id, description=value, app_name=app_name, model_name=model_name)

        if str(field_name) == "workcenter_id":
            attachment_saves.workcenter_id = value
        attachment_saves.save()

        # document_service.Attachment.update_attachment(**attachment_es_update)

        attachments = attachment.objects.filter(object_id=object_id, deleted=False).order_by("id")

        response = {
            "data": [],
        }
        for attachment in attachments:
            response["data"].append(get_attchment_object(attachment))
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception(e)
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


@check_view_permission([{"attachments": "mo_documents"}])
def documents(request):

    user_id = request.user.id
    user = User.objects.get(id=user_id)
    perms = ["can_add_update"]
    permissions = Util.get_permission_role(user, perms)
    tags = Tag.objects.all()
    tag_list = []
    for tag in tags:
        tag_name = get_hierarchy_tag(tag, tag.name)
        tag_list.append(tag_name)

    return render(request, "attachment/documents.html", {"permissions": json.dumps(permissions), "tag_list": tag_list})


def document(request, type=None, id=None):
    try:
        if type == "edit":
            model = apps.get_model("base", "base_attachment")
            document_data = model.objects.filter(id=id).first()
            HtmlFile = open(settings.MEDIA_ROOT + str(document_data.url), "r")
            source_code = HtmlFile.read()
            base_attac_tag_obj = BaseAttachmentTag.objects.filter(attachment_id=id).values_list("tag_id", flat=True).distinct()

            return render(
                request,
                "attachment/document.html",
                {"document_data": document_data, "source_code": source_code, "base_attac_tag_obj": ",".join(str(x) for x in base_attac_tag_obj)},
            )
        return render(request, "attachment/document.html")
    except Exception as e:
        logging.exception(e)
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def document_save(request):
    try:
        id = int(request.POST.get("id"))

        title = request.POST.get("title")
        title = re.sub("[^a-zA-Z0-9_ ]", "", title)
        file_name = title.rstrip() + ".html"
        template = request.POST.get("template")
        todays_date = date.today()
        file_path = (
            connection.tenant.schema_name
            + "\\"
            + "base"
            + "\\"
            + "base"
            + "\\"
            + str(todays_date.year)
            + "\\"
            + str(todays_date.month)
            + "\\"
            + str(todays_date.day)
            + "\\"
            + file_name
        )
        description = request.POST.get("description")

        app_name = "base"
        model_name = "base_attachment"
        ip_addr = get_client_ip(request)

        model = apps.get_model(app_name, model_name)

        file_type_ref = FileType.objects.filter(name="Document").first().id
        u_id = request.user.id
        name = title.rstrip() + ".pdf"
        # todays_date = date.today()
        es_attachment = Document()
        if id is not None and int(id) not in [0, -1]:
            attachment = model.objects.filter(id=id).first()
            with open(settings.MEDIA_ROOT + str(attachment.url), "w") as docfile:
                docfile.write(template)
            size = os.stat(settings.MEDIA_ROOT + str(attachment.url)).st_size
            if size > 10000000:
                return HttpResponse(AppResponse.msg(0, "File more than 10MB size is not allowed."), content_type="json")
            attachment.name = name
            attachment.size = size
            attachment.title = request.POST.get("title")
            attachment.description = description
            attachment.ip_addr = ip_addr
            attachment.user_id = u_id
            msg = "Document updated"
            attachment.save()
            Document().insert([attachment], app_name=app_name, model_name=model_name, status="update")
            log_views.insert(app_name, model_name, [attachment.id], AuditAction.INSERT, u_id, ip_addr, name + " Updtaed file.")
        else:
            path = (
                connection.tenant.schema_name
                + "/base/base/"
                + "{}/{}/{}/".format(str(datetime.date.today().year), str(datetime.date.today().month), str(datetime.date.today().day))
            )
            folder_path = os.path.join(settings.MEDIA_ROOT, str(path))
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            with open(settings.MEDIA_ROOT + file_path, "w") as docfile:
                docfile.write(template)

            size = os.stat(settings.MEDIA_ROOT + file_path).st_size / 1024

            if size > 10000000:
                return HttpResponse(AppResponse.msg(0, "File more than 10MB size is not allowed."), content_type="json")
            attachment = model(
                name=name,
                object_id=0,
                url=file_path,
                size=size,
                title=request.POST.get("title"),
                description=description,
                ip_addr=ip_addr,
                checksum="-",
                user_id=u_id,
                doc_type="gen",
                file_type_id=file_type_ref,
                is_public=False,
                source_doc="",
            )

            path = (
                connection.tenant.schema_name
                + "\\"
                + "base"
                + "\\"
                + "base"
                + "\\"
                + str(todays_date.year)
                + "\\"
                + str(todays_date.month)
                + "\\"
                + str(todays_date.day)
                + "\\"
                + attachment.uid
                + "_"
                + file_name
            )
            attachment.url = path
            new_file_path = settings.MEDIA_ROOT + path
            os.rename(settings.MEDIA_ROOT + file_path, new_file_path)
            msg = "Document saved"
            attachment.save()
            Document().insert([attachment], app_name=app_name, model_name=model_name)
            log_views.insert(app_name, model_name, [attachment.id], AuditAction.INSERT, u_id, ip_addr, name + " uploaded.")
        tag_ids = request.POST.getlist("tag")

        modelname = app_name + "AttachmentTag"
        model = apps.get_model(app_name, modelname)
        base_doc_tag = model.objects.filter(attachment_id=attachment.id)
        base_doc_tag.delete()
        tags = []
        for tag_id in tag_ids:
            tags.append({"id": int(tag_id)})
            model.objects.create(tag_id=int(tag_id), attachment_id=attachment.id)
        es_attachment.update_attachment(attachment_id=attachment.id, title=request.POST.get("title"), description=description, tags=tags, app_name=app_name, model_name=model_name)
        log_views.insert(app_name, model_name, [attachment.id], AuditAction.INSERT, u_id, ip_addr, name + " uploaded.")

        return HttpResponse(json.dumps({"code": 1, "msg": msg, "id": attachment.id}), content_type="json")
    except Exception as e:
        logging.exception(e)
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def tags(request):
    return render(request, "attachment/tags.html")


def tag_search(request):
    try:
        request.POST = Util.get_post_data(request)
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        sort_col = Util.get_sort_column(request.POST)
        query = Q()

        if request.POST.get("name__icontains") is not None:
            query.add(Q(name__icontains=str(request.POST.get("name__icontains"))), query.connector)

        recordsTotal = Tag.objects.filter(query).count()
        tags = Tag.objects.filter(query).order_by(sort_col)[start : (start + length)]
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }

        for tag in tags:
            response["data"].append({"id": tag.id, "name": tag.name, "created_on": Util.get_local_time(tag.created_on), "created_by": tag.created_by.username})

        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong!")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def tag(request, id=None):
    try:
        if request.method == "POST":
            id = request.POST.get("id")
            name = request.POST.get("name")
            parent = request.POST.get("parent")
            c_ip = base_views.get_client_ip(request)
            user_id = request.user.id
            if id is None or (Util.is_integer(id) and int(id) in [0, -1]):
                if Tag.objects.filter(name__iexact=name).count() > 0:
                    return HttpResponse(AppResponse.get({"code": 0, "msg": "Tag name already exists."}), content_type="json")
                base_attach_tag = Tag.objects.create(name=name, created_by_id=user_id, parent_id=parent)
                action = AuditAction.INSERT
                log_views.insert("attachment", "tag", [base_attach_tag.id], action, user_id, c_ip, name + " Inserted")
                return HttpResponse(json.dumps({"code": 1, "msg": "Tag saved.", "id": base_attach_tag.id}), content_type="json")
            else:
                tag = Tag.objects.get(id=int(id))
                if Tag.objects.filter(name__iexact=name).exclude(name__iexact=tag.name).count() > 0:
                    return HttpResponse(AppResponse.get({"code": 0, "msg": "Tag name already exists."}), content_type="json")
                base_attach_tag = Tag.objects.filter(id=id).update(name=name, created_by_id=user_id, parent_id=parent)
                action = AuditAction.UPDATE
                log_views.insert("attachment", "tag", [id], action, user_id, c_ip, name + " Updated")
                return HttpResponse(json.dumps({"code": 1, "msg": "Tag saved.", "id": tag.id}), content_type="json")
        else:
            tag_data = Tag.objects.filter(id=id).first()
            return render(request, "attachment/tag.html", {"tag_data": tag_data})
    except Exception as e:
        logging.exception("Something")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def check_tag_use(request):
    try:
        post_ids = request.POST.get("ids")

        ids = [int(x) for x in post_ids.split(",")]

        tag_id = BaseAttachmentTag.objects.filter(tag_id__in=ids)
        in_use = False

        if len(tag_id) > 0:
            in_use = True

        return HttpResponse(json.dumps({"code": 1, "data": in_use}), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, "Error occurred."), content_type="json")


def tag_del(request):
    try:
        post_ids = request.POST.get("ids")

        if not post_ids:
            return HttpResponse(AppResponse.msg(0, "Please select atleast one record."), content_type="json")

        ids = [int(x) for x in post_ids.split(",")]

        base_attacg_tag_delete = BaseAttachmentTag.objects.filter(tag_id__in=ids)
        base_attacg_tag_delete.delete()

        tag_delete = Tag.objects.filter(id__in=ids)
        tag_delete.delete()

        return HttpResponse(json.dumps({"code": 1, "msg": "Data removed."}), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, "Error occurred."), content_type="json")


def get_hierarchy_tag(tag, tag_name):
    if tag.parent_id is None:
        return tag_name
    else:
        tag_name = tag.parent.name + "/" + tag_name
        sub_tag = tag.parent
        return get_hierarchy_tag(sub_tag, tag_name)


def save_doc_tag(request):
    try:
        attachment_id = int(request.POST.get("attachment_id"))
        app_name = request.POST.get("app_name")
        model_name = request.POST.get("model_name")
        tag_id_list = request.POST.get("tag_list")
        es_attachment = Document()
        tags = []

        modelname = model_name
        modelname = modelname.replace("_", "")
        modelname = modelname + "Tag"

        model = apps.get_model(app_name, modelname)
        base_doc_tag = model.objects.filter(attachment_id=attachment_id)
        base_doc_tag.delete()
        data = []
        if tag_id_list != "":
            tad_ids = [int(x) for x in tag_id_list.split(",")]

            for tad_id in tad_ids:
                model.objects.create(attachment_id=attachment_id, tag_id=tad_id)
                tags.append({"id": tad_id})
            attachment_tags = Tag.objects.filter(id__in=tad_ids)
            for tag in attachment_tags:
                tag_name = get_hierarchy_tag(tag, tag.name)
                data.append({"id": tag.id, "name": tag_name})
        es_attachment.update_attachment(attachment_id=attachment_id, tags=tags, app_name=app_name, model_name=model_name)
        return HttpResponse(json.dumps({"code": 1, "msg": "", "data": data}), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, "Error occurred."), content_type="json")
