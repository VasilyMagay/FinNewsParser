"""
mainapp/management/commands/init_sites.py
"""
from collections import namedtuple
from django.core.management.base import BaseCommand
from mainapp.models import Site

SiteInfo = namedtuple('SiteInfo', 'name ref descr')

SITES_INFO = [
    SiteInfo(
        name='Финам',
        ref='https://www.finam.ru/analysis/united/',
        descr='Объединенная лента финансовых новостей и событий'
    )
]


class Command(BaseCommand):
    """
    Fill information about sites
    """
    help = 'Fill information about sites'

    def handle(self, *args, **options):
        Site.objects.all().delete()
        site_new = 0
        for site_info in SITES_INFO:
            Site.objects.create(
                name=site_info.name,
                ref=site_info.ref,
                descr=site_info.descr,
            ).save()
            site_new += 1
        print('Insert {} sites'.format(site_new))
