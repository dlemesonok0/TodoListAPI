from rest_framework import serializers

from todolist.models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('id',)
        extra_kwargs = {
            'description': {'required': False},
            'done': {'required': False},
            'date': {'required': False},
        }

    def validate_title(self, title):
        if title == '':
            raise serializers.ValidationError('Нет названия')
        return title