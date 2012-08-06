import os

from django.core.management.base import BaseCommand, CommandError

from quarterback.fecmaster.importer import *


class Command(BaseCommand):
    args = ''
    help = 'delete records for the latest cycle and redownload and re-insert'

    def handle(self, *args, **options):
        
        start = unicode(cycles[-1])[-2:]
        
        config = cycle_config(start)
        i = FECImporter('~/working/datacommons',config)
        i.update_csv()
        i.update_db()
        
        os.system("psql datacommons < fecmaster/postload.sql")
