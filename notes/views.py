from rest_framework.generics import GenericAPIView
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Note, NoteUpdate
from .serializers import NoteSerializer, ShareNoteSerializer, NoteUpdateSerializer, NoteVersionHistorySerializer

class CreateNoteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = NoteSerializer(data=request.data, context={'request': request })
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RetrieveNoteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        try:
            note = Note.objects.get(id=id)
            if note.owner == request.user or request.user in note.shared_with.all():
                serializer = NoteSerializer(note)
                return Response(serializer.data)
            else:
                return Response({"message": "Not authorized to view this note"}, status=status.HTTP_403_FORBIDDEN)
        except Note.DoesNotExist:
            return Response({ "message": "Note not found" }, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, id):
        try:
            note = Note.objects.get(pk=id)
        except Note.DoesNotExist:
            return Response({ "error": "Note not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user != note.owner and request.user not in note.shared_with.all():
            return Response({ "error": "You do not have permission to update this note."}, status=status.HTTP_403_FORBIDDEN)
        serializer = NoteUpdateSerializer(data=request.data, context={'request': request, 'note_id': id})
        if serializer.is_valid():
            serializer.save()
            return Response({ "message": "Note updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ShareNoteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ShareNoteSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({ "message": "Note shared successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class NoteVersionHistoryView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NoteVersionHistorySerializer

    def get(self, request, id):
        try:
            note = Note.objects.get(pk=id)
        except Note.DoesNotExist:
            return Response({ "error": "Note not found." }, status=status.HTTP_404_NOT_FOUND)
        
        if request.user != note.owner and request.user not in note.shared_with.all():
            return Response({ "error": "You do not have permission to view this note's history."}, status=status.HTTP_403_FORBIDDEN)
        
        updates = NoteUpdate.objects.filter(note=note).order_by('-timestamp')
        serializer = self.get_serializer(updates, many=True)
        return Response(serializer.data)