"""
Management utility to create Players Types.
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from players.models import Positions, PositionGroup

User = get_user_model()


class Command(BaseCommand):
    help = 'Used to create add relation between position and position groups.'

    def handle(self, *args, **options):
        all_positions = Positions.objects.all()
        try:
            position_group = PositionGroup.objects.get(
                    name__iexact="Edge Rushers"
                )
        except PositionGroup.DoesNotExist:
            position_group = PositionGroup.objects.create(
                    name="Edge Rushers"
                )
        active_groups = ['DB', 'R', 'RB', 'Edge Rushers', 'LB']
        for pos in active_groups:
            pos_grp = PositionGroup.objects.get(name__iexact=pos)
            pos_grp.status = 'active'
            pos_grp.save()

        for position in all_positions:
            pos = position.name
            db = ['CB', 'S', 'SS', 'FS', 'DB']
            rb = ['APB', 'RB', 'FB']
            rec = ['WR', 'TE', 'R', 'T']
            ol = ['OL', 'OT', 'OG', 'OC']
            dl = ['DL', 'WDE', 'SDE', 'DT']
            lb = ['LB', 'ILB', 'OLB']
            qb = ['Pro', 'PRO', 'Dual', 'DUAL', 'QB']
            Special = ['ATH', 'K', 'P', 'LS', 'RET']
            if pos in db:
                pos_group = 'DB'
            elif pos in rb:
                pos_group = 'RB'
            elif pos in rec:
                pos_group = 'R'
            elif pos in ol:
                pos_group = 'OL'
            elif pos in dl:
                pos_group = 'DL'
            elif pos in lb:
                pos_group = 'LB'
            elif pos in qb:
                pos_group = 'QB'
            elif pos in Special:
                pos_group = 'Special'
            else:
                pos_group = None
            if pos_group != None:
                position.groups.clear()
                try:
                    position_group = PositionGroup.objects.get(
                        name__iexact=pos_group
                    )
                except PositionGroup.DoesNotExist:
                    position_group = PositionGroup.objects.create(
                        name=pos_group
                    )
                position.groups.add(position_group)
            if pos in ['OLB','WDE']:
                position_group = PositionGroup.objects.get(
                    name__iexact="Edge Rushers"
                )
                position.groups.add(position_group)
