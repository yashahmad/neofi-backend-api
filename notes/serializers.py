from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Note, NoteUpdate

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'owner', 'shared_with', 'created_at', 'updated_at',]
        extra_kwargs = { 'owner': { 'read_only': True }}

class NoteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteUpdate
        fields = ['content']

    def create(self, validated_data):
        note_id = self.context['note_id']
        user = self.context['request'].user
        note = Note.objects.get(pk=note_id)
        update = NoteUpdate.objects.create(note=note, changed_by=user, **validated_data)
        return update

class NoteVersionHistorySerializer(serializers.ModelSerializer):
    changed_by = serializers.StringRelatedField()

    class Meta:
        model = NoteUpdate
        fields = ['changed_by', 'content', 'timestamp']

class ShareNoteSerializer(serializers.Serializer):
    note_id = serializers.IntegerField(min_value=1, write_only=True)
    user_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
        write_only=True
    )

    def validate_note_id(self, value):
        user = self.context['request'].user
        if not Note.objects.filter(id=value, owner=user).exists():
            raise serializers.ValidationError("Note not found or you're not the owner.")
        return value

    def update(self, instance, validated_data):
        user_ids = validated_data.get('user_ids')
        users = User.objects.filter(id__in=user_ids)
        for user in users:
            instance.shared_with.add(user)
        instance.save()
        return instance

    def save(self, **kwargs):
        note_id = self.validated_data['note_id']
        user_ids = self.validated_data['user_ids']
        note = Note.objects.get(id=note_id)
        users = User.objects.filter(id__in=user_ids)
        for user in users:
            note.shared_with.add(user)
        note.save()