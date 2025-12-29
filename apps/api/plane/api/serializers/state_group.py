from .base import BaseSerializer
from plane.db.models import StateGroup

class StateGroupSerializer(BaseSerializer):
    class Meta:
        model = StateGroup
        fields = "__all__"
        read_only_fields = ["workspace"]