from rest_framework import viewsets, status
from rest_framework.response import Response
from plane.db.models import StateGroup
from plane.api.serializers.state_group import StateGroupSerializer
from plane.api.permissions import WorkSpaceAdminPermission

class StateGroupViewSet(viewsets.ModelViewSet):
    permission_classes = [WorkSpaceAdminPermission]
    serializer_class = StateGroupSerializer
    model = StateGroup

    def get_queryset(self):
        return self.request.user.workspace.state_groups.all().order_by("sequence")

    def perform_create(self, serializer):
        serializer.save(workspace_id=self.kwargs.get("slug"))

    def destroy(self, request, slug, pk=None):
        instance = self.get_object()
        if instance.states.filter(deleted_at__isnull=True).exists():
            return Response(
                {"error": "Cannot delete group containing active states."},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)