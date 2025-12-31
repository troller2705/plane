from rest_framework import viewsets, status
from rest_framework.response import Response
from plane.db.models import StateGroup, Workspace
from plane.api.serializers.state_group import StateGroupSerializer
# Corrected Import:
from plane.app.permissions import WorkSpaceAdminPermission

class StateGroupViewSet(viewsets.ModelViewSet):
    permission_classes = [WorkSpaceAdminPermission]
    serializer_class = StateGroupSerializer
    model = StateGroup

    def get_queryset(self):
        return StateGroup.objects.filter(
            workspace__slug=self.kwargs.get("slug")
        ).order_by("sequence")

    def perform_create(self, serializer):
        workspace = Workspace.objects.get(slug=self.kwargs.get("slug"))
        serializer.save(workspace=workspace)

    def destroy(self, request, slug, pk=None):
        instance = self.get_object()
        # Prevent deletion if states are using this group
        if instance.states.filter(deleted_at__isnull=True).exists():
             return Response(
                {
                    "error": "Cannot delete group containing active states.",
                    "message": "Please move existing states to another group before deleting this one."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
