from django.urls import path

from .views import (
    ChatIAJsonView,
    ConsumoIAListView,
    ConversaDetailView,
    ConversaListView,
)

app_name = "ia"

urlpatterns = [
    path("conversas/", ConversaListView.as_view(), name="conversa-list"),
    path("conversas/<int:pk>/", ConversaDetailView.as_view(), name="conversa-detail"),
    path("chat/", ChatIAJsonView.as_view(), name="chat"),
    path("conversas/<int:pk>/chat/", ChatIAJsonView.as_view(), name="chat-conversa"),
    path("consumo/", ConsumoIAListView.as_view(), name="consumo-list"),
]
