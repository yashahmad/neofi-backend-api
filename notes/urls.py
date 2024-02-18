from django.urls import path
from .views import CreateNoteView, RetrieveNoteView, ShareNoteView, NoteVersionHistoryView

urlpatterns = [
    path('create', CreateNoteView.as_view(), name='create_note'),
    path('<int:id>', RetrieveNoteView.as_view(), name='retrieve_note'),
    path('share', ShareNoteView.as_view(), name='share_note'),
    path('version-history/<int:id>', NoteVersionHistoryView.as_view(), name='note_version_history'),
]
