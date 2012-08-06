import os
import subprocess
import urllib
import time 

from collections import namedtuple
from log import set_up_logger
from django.db import connection


F = namedtuple('F', ['url', 'filename', 'schema', 'sql_table','cycle'])


cycle_ints = range(1980,2014,2)
cycles = [unicode(x)[-2:] for x in cycle_ints]
    
def long_cycle(cycle):
    if int(cycle)>60: return '19' + cycle
    return '20'+cycle
    
def cycle_config(cycle):
    return [
        F('ftp://ftp.fec.gov/FEC/%s/indiv%s.zip' % (long_cycle(cycle), cycle), 'itcont.txt', None, 'fec_indiv', long_cycle(cycle)),
        F('ftp://ftp.fec.gov/FEC/%s/pas2%s.zip' % (long_cycle(cycle), cycle), 'itpas2.txt', None, 'fec_pac2cand', long_cycle(cycle)),
        F('ftp://ftp.fec.gov/FEC/%s/oth%s.zip' % (long_cycle(cycle), cycle), 'itoth.txt', None, 'fec_pac2pac', long_cycle(cycle)),
        F('ftp://ftp.fec.gov/FEC/%s/cm%s.zip' % (long_cycle(cycle), cycle), 'cm.txt', 'fec_committee_master_schema.csv', 'fec_committees',  long_cycle(cycle)),
        F('ftp://ftp.fec.gov/FEC/%s/cn%s.zip' % (long_cycle(cycle), cycle), 'cn.txt', 'fec_candidate_master_schema.csv', 'fec_candidates', long_cycle(cycle)),
        F('ftp://ftp.fec.gov/FEC/%s/webl%s.zip' % (long_cycle(cycle), cycle), 'webl%s.txt' % cycle, 'fec_candidate_summary.csv', 'fec_candidate_summaries', long_cycle(cycle)),
        F('ftp://ftp.fec.gov/FEC/%s/webk%s.zip' % (long_cycle(cycle), cycle), 'webk%s.txt' % cycle, 'fec_pac_summary.csv', 'fec_committee_summaries', long_cycle(cycle))
    ]


SQL_PRELOAD_FILE = os.path.join(os.path.dirname(__file__), 'preload.sql')
SQL_POSTLOAD_FILE = os.path.join(os.path.dirname(__file__), 'postload.sql')

FEC_CONFIG = cycle_config('12')

class FECImporter():
    def __init__(self, processing_dir, config=FEC_CONFIG):
        self.processing_dir = os.path.expanduser(processing_dir)
        self.FEC_CONFIG = config

        self.log = set_up_logger('fec_importer', self.processing_dir, 'Unhappy FEC Importer')


    def update_csv(self):
        try:
            self.log.info("Downloading files to %s..." % self.processing_dir)
            self.download()

            self.log.info("Extracting files...")
            self.extract()

            self.log.info("Converting to unicode...")
            self.fix_unicode()

        except Exception as e:
            self.log.error(e)
            raise


    def update_db(self):
        try:
            c = connection.cursor()

            self.log.info("Uploading data...")
            self.upload(c)

            self.log.info("Done.")
        except Exception as e:
            self.log.error(e)
            raise

    def _download_file(self, conf):
        filename = conf.url.split("/")[-1]
        dirname = filename.split(".")[0]
        return os.path.join(self.processing_dir, dirname, filename)
        
    def _working_dir(self, conf):
        filename = conf.url.split("/")[-1]
        dirname = filename.split(".")[0]
        return os.path.join(self.processing_dir, dirname)

    def download(self):
        for conf in self.FEC_CONFIG:
            if not os.path.isdir(self._working_dir(conf)):
                os.makedirs(self._working_dir(conf))

            self.log.info("downloading %s to %s..." % (conf.url, self._download_file(conf)))
            urllib.urlretrieve(conf.url, self._download_file(conf))


    def extract(self):
        for conf in self.FEC_CONFIG:
            subprocess.check_call(['unzip', '-oqu', self._download_file(conf), "-d" + self._working_dir(conf)])


    def fix_unicode(self):
        for conf in self.FEC_CONFIG:
            try:
                infile = open(os.path.join(self._working_dir(conf), conf.filename), 'r')
            except:
                infile = open(os.path.join(self._working_dir(conf), conf.filename)[:-3]+'dta', 'r')
            
            outfile = open(os.path.join(self._working_dir(conf), conf.filename[:-3] + "txt.utf8"), 'w')

            for line in infile:
                try:
                    fixed_line = line.decode('utf8', 'replace').encode('utf8', 'replace')
                except:
                    fixed_line = line
                    self.log.info('utf problem' + line)
                    continue #don't include this line in the database (!)
                
                if not conf.schema:
                    parts = fixed_line.split('|')
                    if len(parts[13])==7:
                        parts[13] = '0' + parts[13][:2] + parts[13][3:]
                    date = parts[13][-4:] + '-' + parts[13][:2] + '-' + parts[13][2:4]
                    try:
                        time.strptime(date,"%Y-%m-%d")
                    except:
                        date = ''
                    parts[13] = date
                    fixed_line = '|'.join(parts)
                try:
                    outfile.write(conf.cycle+'|'+fixed_line)
                except:
                    self.log.info('couldnt write ' + fixed_line)

    def execute_file(self, cursor, filename):
        print 'executing ' + filename
        contents = " ".join([line for line in open(filename, 'r') if line[0:2] != '--'])
        statements = contents.split(';')[:-1] # split on semi-colon. Last element will be trailing whitespace

        for statement in statements:
            self.log.info("Executing %s" % statement)
            cursor.execute(statement)


    def upload(self, c):

        for conf in self.FEC_CONFIG:
            infile = os.path.join(self._working_dir(conf), conf.filename + '.utf8')
            c.execute("DELETE FROM %s WHERE cycle=%s" % (conf.sql_table, conf.cycle))
            # note: quote character is an arbitrary ASCII code that is unlikely to appear in data.
            # FEC uses single and double quotes and most other printable characters in the data,
            # so we have to be sure not to misinterpret any of them as semantically meaningful.
            os.system("""psql datacommons -c "COPY %s FROM '%s' CSV HEADER DELIMITER '|' QUOTE E'\\x1F';\"""" % (conf.sql_table, infile))
