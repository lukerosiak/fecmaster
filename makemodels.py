"""Not currently used in this app, but scrapes the schema of tables from FEC's web site and generates django models."""

import re
import urllib2
from BeautifulSoup import BeautifulSoup


re_char = re.compile('VARCHAR2\s*\((\d+)(?: Byte)?\)')
def getdatatype(fec):
    if re_char.match(fec):
        return 'Char', re_char.match(fec).groups()[0]
    if re.match('NUMBER\s*\(\d+\)',fec):
        return 'Integer',None
    if re.match('NUMBER\s*\(\d+,\d\)',fec):
        return 'Float',None
    if re.match('DATE',fec):
        return 'Date',None
    return 'unknown',None


def unsoupify(cell):
    if not cell.contents or not cell.contents[0]:
        return ''
    return unicode(cell.contents[0]).strip().replace('"','')


tables = {
    'cm': 'CommitteeMaster',
    'cn': 'CandidateMaster',
    'ccl': 'CandCmteLinkage',
    'indiv': 'ContributionsbyIndividuals',
    'pas': 'ContributionstoCandidates',
    'oth': 'CommitteetoCommittee',
    'weball': 'WEBALL',
    'weballk': 'WEBK',
}

def writemodels():

    fout = open('models.py','w')
    fout.write("from django.db import models\n\n\n")


    for key in tables.keys():
        html = urllib2.urlopen('http://www.fec.gov/finance/disclosure/metadata/DataDictionary%s.shtml' % tables[key]).read()
        soup = BeautifulSoup(html).table.findAll('tr')[1:]

        fout.write("""


class %s(models.Model):
    class Meta:
        verbose_name="%s"
    cycle = models.IntegerField()
""" % (key, tables[key]))


        for row in soup:
            cells = row.findAll('td')
            (name,longname,start,isnull,datatype,descrip) = [unsoupify(x) for x in cells]
            (djangotype,length) = getdatatype(datatype)
            
            if djangotype=='Char':
                fout.write("""
    %s = models.CharField(max_length=%s, blank=True, verbose_name="%s", help_text = "%s")""" % (name,length,longname,descrip)) 
            elif djangotype=='Date':
                fout.write("""
    %s = models.DateField(blank=True, verbose_name="%s", help_text = "%s")"""  % (name,longname,descrip)) 
            elif djangotype=='Integer':
                fout.write("""
    %s = models.IntegerField(verbose_name="%s", help_text = "%s")""" % (name,longname,descrip)) 
            elif djangotype=='Float':
                fout.write("""
    %s = models.FloatField(verbose_name="%s", help_text = "%s")""" % (name,longname,descrip)) 



    
writemodels()
