from django.core.management.base import BaseCommand
from mainapp.models import Site
from collections import namedtuple

SiteInfo = namedtuple('SiteInfo', 'name ref descr')

sites_info = [
    SiteInfo(
        name='Финам',
        ref='https://www.finam.ru/analysis/united/',
        descr='Объединенная лента финансовых новостей и событий'
    )
]


class Command(BaseCommand):
    help = 'Fill information about sites'

    def handle(self, *args, **options):

        Site.objects.all().delete()
        site_new = 0
        for site_info in sites_info:
            Site.objects.create(
                name=site_info.name,
                ref=site_info.ref,
                descr=site_info.descr,
            ).save()
            site_new += 1
        print('Insert {} sites'.format(site_new))
