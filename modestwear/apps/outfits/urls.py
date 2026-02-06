from django.urls import path
from .api.views import (
    OutfitListCreateView,
    OutfitDetailView,
    PublicOutfitListView,
    add_item_to_outfit,
    remove_item_from_outfit
)

app_name = 'outfits'

urlpatterns = [
    path('', OutfitListCreateView.as_view(), name='outfit-list-create'),
    path('<int:pk>/', OutfitDetailView.as_view(), name='outfit-detail'),
    path('public/', PublicOutfitListView.as_view(), name='public-outfits'),
    path('<int:outfit_id>/items/', add_item_to_outfit, name='add-item'),
    path('<int:outfit_id>/items/<int:item_id>/', remove_item_from_outfit, name='remove-item'),
]