from django.urls import path

# View imports
from plane.api.views.state_group import StateGroupViewSet

# URL Patterns imports - ONLY importing files that exist in apps/api/plane/api/urls/
from .asset import urlpatterns as asset_urls
from .cycle import urlpatterns as cycle_urls
from .intake import urlpatterns as intake_urls
from .invite import urlpatterns as invite_urls
from .label import urlpatterns as label_urls
from .member import urlpatterns as member_urls
from .module import urlpatterns as module_urls
from .project import urlpatterns as project_urls
from .state import urlpatterns as state_urls
from .sticky import urlpatterns as sticky_urls
from .user import urlpatterns as user_urls
from .work_item import urlpatterns as work_item_urls

# Define the new State Group endpoints
urlpatterns = [
    path(
        "workspaces/<str:slug>/state-groups/", 
        StateGroupViewSet.as_view({'get': 'list', 'post': 'create'}), 
        name="workspace-state-groups"
    ),
    path(
        "workspaces/<str:slug>/state-groups/<uuid:pk>/", 
        StateGroupViewSet.as_view({'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), 
        name="workspace-state-groups-detail"
    ),
]

# Append existing patterns
urlpatterns += asset_urls
urlpatterns += cycle_urls
urlpatterns += intake_urls
urlpatterns += invite_urls
urlpatterns += label_urls
urlpatterns += member_urls
urlpatterns += module_urls
urlpatterns += project_urls
urlpatterns += state_urls
urlpatterns += sticky_urls
urlpatterns += user_urls
urlpatterns += work_item_urls
