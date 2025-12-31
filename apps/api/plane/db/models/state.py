# Django imports
from django.db import models
from django.template.defaultfilters import slugify
from django.db.models import Q

# Module imports
from plane.db.models import BaseModel
from .project import ProjectBaseModel
from plane.db.mixins import SoftDeletionManager

# --- Compatibility Layer ---
# Allows StateGroup.BACKLOG.value to work while StateGroup is a Model
class StateValue(str):
    @property
    def value(self):
        return self

class StateGroup(BaseModel):
    """
    New Dynamic State Group Model replacing the old Enum for DB storage.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sequence = models.FloatField(default=65535)
    # FIX: Changed 'plane.Workspace' to 'db.Workspace'
    workspace = models.ForeignKey(
        "db.Workspace", 
        related_name="state_groups", 
        on_delete=models.CASCADE
    )
    icon = models.CharField(max_length=255, default="lucide:circle", blank=True)

    # Constants for backward compatibility
    BACKLOG = StateValue("backlog")
    UNSTARTED = StateValue("unstarted")
    STARTED = StateValue("started")
    COMPLETED = StateValue("completed")
    CANCELLED = StateValue("cancelled")
    TRIAGE = StateValue("triage")

    choices = (
        (BACKLOG, "Backlog"),
        (UNSTARTED, "Unstarted"),
        (STARTED, "Started"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
        (TRIAGE, "Triage"),
    )

    SYSTEM_STAGES = choices 
    system_stage = models.CharField(choices=SYSTEM_STAGES, max_length=20, default=UNSTARTED)

    class Meta:
        verbose_name = "State Group"
        verbose_name_plural = "State Groups"
        unique_together = ["workspace", "name"]
        db_table = "plane_state_group"
        ordering = ["sequence", "name"]

    def __str__(self):
        return f"{self.name}"

# --- Original Managers ---

class StateManager(SoftDeletionManager):
    """Default manager - excludes triage states"""
    def get_queryset(self):
        return super().get_queryset().exclude(group=StateGroup.TRIAGE)

class TriageStateManager(SoftDeletionManager):
    """Manager for triage states only"""
    def get_queryset(self):
        return super().get_queryset().filter(group=StateGroup.TRIAGE)

class State(ProjectBaseModel):
    name = models.CharField(max_length=255, verbose_name="State Name")
    description = models.TextField(verbose_name="State Description", blank=True)
    color = models.CharField(max_length=255, verbose_name="State Color")
    slug = models.SlugField(max_length=100, blank=True)
    sequence = models.FloatField(default=65535)
    
    # Legacy field
    group = models.CharField(
        choices=StateGroup.choices,
        default=StateGroup.BACKLOG,
        max_length=20,
    )

    # --- NEW FIELDS ---
    group_link = models.ForeignKey(
        "StateGroup", 
        related_name="states", 
        on_delete=models.RESTRICT, 
        null=True
    )
    icon = models.CharField(max_length=255, null=True, blank=True)
    # ------------------

    is_triage = models.BooleanField(default=False)
    default = models.BooleanField(default=False)
    external_source = models.CharField(max_length=255, null=True, blank=True)
    external_id = models.CharField(max_length=255, blank=True, null=True)

    # Managers
    objects = StateManager()
    all_state_objects = models.Manager() 
    triage_objects = TriageStateManager()

    def __str__(self):
        return f"{self.name} <{self.project.name}>"

    class Meta:
        unique_together = ["name", "project", "deleted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "project"],
                condition=Q(deleted_at__isnull=True),
                name="state_unique_name_project_when_deleted_at_null",
            )
        ]
        verbose_name = "State"
        verbose_name_plural = "States"
        db_table = "states"
        ordering = ("sequence",)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        if self._state.adding:
            last_id = State.objects.filter(project=self.project).aggregate(largest=models.Max("sequence"))["largest"]
            if last_id is not None:
                self.sequence = last_id + 15000

        return super().save(*args, **kwargs)

# --- Default States ---
DEFAULT_STATES = [
    {
        "name": "Backlog",
        "color": "#60646C",
        "sequence": 15000,
        "group": StateGroup.BACKLOG,
        "default": True,
    },
    {
        "name": "Todo",
        "color": "#60646C",
        "sequence": 25000,
        "group": StateGroup.UNSTARTED,
    },
    {
        "name": "In Progress",
        "color": "#F59E0B",
        "sequence": 35000,
        "group": StateGroup.STARTED,
    },
    {
        "name": "Done",
        "color": "#46A758",
        "sequence": 45000,
        "group": StateGroup.COMPLETED,
    },
    {
        "name": "Cancelled",
        "color": "#9AA4BC",
        "sequence": 55000,
        "group": StateGroup.CANCELLED,
    },
    {
        "name": "Triage",
        "color": "#4E5355",
        "sequence": 65000,
        "group": StateGroup.TRIAGE,
    },
]
