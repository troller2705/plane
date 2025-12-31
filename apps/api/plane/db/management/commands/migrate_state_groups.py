from django.core.management.base import BaseCommand
from plane.db.models import Workspace, State, StateGroup

class Command(BaseCommand):
    help = "Migrate existing States to Dynamic State Groups"

    def handle(self, *args, **options):
        workspaces = Workspace.objects.all()
        self.stdout.write(f"Found {workspaces.count()} workspaces to migrate.")

        for workspace in workspaces:
            self.stdout.write(f"Processing workspace: {workspace.name}")
            
            # 1. Create Default Groups for this Workspace
            groups = {}
            defaults = [
                ("Backlog", "backlog", 1000),
                ("Unstarted", "unstarted", 2000),
                ("Started", "started", 3000),
                ("Completed", "completed", 4000),
                ("Cancelled", "cancelled", 5000),
                ("Triage", "triage", 500),
            ]

            for name, slug, seq in defaults:
                group, created = StateGroup.objects.get_or_create(
                    workspace=workspace,
                    system_stage=slug,
                    defaults={
                        "name": name,
                        "sequence": seq,
                        "description": f"Default {name} group"
                    }
                )
                groups[slug] = group

            # 2. Link Existing States to these Groups
            # We map the old 'group' string field to the new 'group_link' foreign key
            states = State.objects.filter(workspace=workspace)
            updated_count = 0
            
            for state in states:
                # The old 'group' field contains strings like 'backlog', 'started'
                target_group = groups.get(state.group)
                if target_group:
                    state.group_link = target_group
                    state.save(update_fields=["group_link"])
                    updated_count += 1
            
            self.stdout.write(f"  - Linked {updated_count} states to groups.")

        self.stdout.write(self.style.SUCCESS("Successfully migrated State Groups!"))
