import os

from django.core.management.base import BaseCommand, CommandError

from quarterback.fecmaster.importer import *


class Command(BaseCommand):
    args = '<start_year (e.g. 2012)>'
    help = 'create database tables and populate them for all cycles starting from the year provided, then add indexes'

    def handle(self, *args, **options):
        
        if len(args): 
            start = args[0]
        else:
            start = cycles[-1]
        
        cycle_ints = range(start,2014,2)
        mycycles = [unicode(x)[-2:] for x in cycle_ints]

        os.system("psql datacommons < fecmaster/create_fec.sql")

        for cycle in mycycles:
            config = cycle_config(cycle)
            i = FECImporter('~/working/datacommons',config)
            i.update_csv()
            i.update_db()
        
        os.system("psql datacommons < fecmaster/postload.sql")
        os.system("psql datacommons < fecmaster/create_index.sql")
