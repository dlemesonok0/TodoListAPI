import json
from typing import List, Dict, Any

from django.db import transaction
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from todolist import serializers
from todolist.models import Task
from todolist.serializers import TaskSerializer


class TodoListView(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = serializers.TaskSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=["post"], url_path="import")
    def import_json(self, request: Request) -> Response:
        try:
            items = self._extract_items(request)
            if not isinstance(items, list):
                return Response(
                    {"detail": "Ожидался JSON-массив задач."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        created = 0
        updated = 0
        skipped = 0
        errors: List[Dict[str, Any]] = []

        with transaction.atomic():
            for idx, payload in enumerate(items):
                if not isinstance(payload, dict):
                    skipped += 1
                    errors.append({"index": idx, "reason": "item is not an object"})
                    continue

                obj_id = payload.get("id", None)

                try:
                    if obj_id is not None:
                        try:
                            instance = Task.objects.get(pk=obj_id)
                        except Task.DoesNotExist:
                            serializer = TaskSerializer(data=payload)
                            if serializer.is_valid():
                                serializer.save()
                                created += 1
                            else:
                                errors.append({"index": idx, "id": obj_id, "errors": serializer.errors})
                        else:
                            serializer = TaskSerializer(instance, data=payload, partial=True)
                            if serializer.is_valid():
                                serializer.save()
                                updated += 1
                            else:
                                errors.append({"index": idx, "id": obj_id, "errors": serializer.errors})
                    else:
                        serializer = TaskSerializer(data=payload)
                        if serializer.is_valid():
                            serializer.save()
                            created += 1
                        else:
                            errors.append({"index": idx, "errors": serializer.errors})
                except Exception as ex:
                    errors.append({"index": idx, "exception": str(ex)})
                    skipped += 1

        report = {
            "created": created,
            "updated": updated,
            "skipped": skipped,
            "errors": errors,
            "total_received": len(items),
        }
        return Response(report, status=status.HTTP_200_OK)

    def _extract_items(self, request: Request) -> List[Dict[str, Any]]:
        if "file" in request.FILES:
            raw = request.FILES["file"].read()
            try:
                data = json.loads(raw.decode("utf-8"))
            except Exception:
                data = json.loads(raw)
            return data

        if isinstance(request.data, list):
            return request.data

        if isinstance(request.data, str):
            return json.loads(request.data)

        if isinstance(request.data, dict) and "items" in request.data:
            return request.data["items"]

        raise ValueError("Не удалось извлечь массив задач. Передайте файл 'file' или JSON-массив в теле запроса.")