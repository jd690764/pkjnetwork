from __future__ import unicode_literals

from django.db import models
import datetime

class Alterations(models.Model):
    alt_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    descr = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'alterations'


class Amps(models.Model):
    cnvid = models.IntegerField()
    cancer_id = models.IntegerField()
    profile_id = models.IntegerField()
    alt_id = models.IntegerField()
    barcode_id = models.IntegerField()
    geneid = models.IntegerField()
    value = models.CharField(max_length=500)

    class Meta:
        managed = False
        db_table = 'amps'


class Barcodes(models.Model):
    barcode_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'barcodes'


class CancerBcs(models.Model):
    barcode_id = models.IntegerField()
    cancer_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'cancer_bcs'


class Cancers(models.Model):
    cancer_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    descr = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cancers'


class Cdd(models.Model):
    pssm = models.IntegerField(db_column='PSSM', primary_key=True)  # Field name made lowercase.
    acc = models.CharField(db_column='ACC', max_length=20)  # Field name made lowercase.
    name = models.CharField(db_column='NAME', max_length=20, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='DESCRIPTION', max_length=2000, blank=True, null=True)  # Field name made lowercase.
    root = models.IntegerField(db_column='ROOT', blank=True, null=True)  # Field name made lowercase.
    sub = models.CharField(db_column='SUB', max_length=5000, blank=True, null=True)  # Field name made lowercase.
    super = models.IntegerField(db_column='SUPER', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'cdd'


class Cnv(models.Model):
    cnvid = models.AutoField(primary_key=True)
    cancer_id = models.IntegerField()
    profile_id = models.IntegerField()
    alt_id = models.IntegerField()
    barcode_id = models.IntegerField()
    geneid = models.IntegerField()
    value = models.CharField(max_length=500)

    class Meta:
        managed = False
        db_table = 'cnv'

    

class Dbsnp(models.Model):
    rsno = models.CharField(primary_key=True, max_length=20)
    taxid = models.IntegerField()
    rstype = models.CharField(max_length=10, blank=True, null=True)
    alleles = models.CharField(max_length=20, blank=True, null=True)
    valid = models.IntegerField(blank=True, null=True)
    assembly = models.CharField(max_length=50, blank=True, null=True)
    chrom = models.CharField(max_length=10, blank=True, null=True)
    chrpos = models.IntegerField(blank=True, null=True)
    symbol = models.CharField(max_length=20, blank=True, null=True)
    eid = models.IntegerField(blank=True, null=True)
    vartype = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dbsnp'
        

class Dels(models.Model):
    cnvid = models.IntegerField()
    cancer_id = models.IntegerField()
    profile_id = models.IntegerField()
    alt_id = models.IntegerField()
    barcode_id = models.IntegerField()
    geneid = models.IntegerField()
    value = models.CharField(max_length=500)

    class Meta:
        managed = False
        db_table = 'dels'


class Emili(models.Model):
    name = models.CharField(max_length=15, blank=True, null=True)
    size = models.IntegerField(blank=True, null=True)
    acc = models.CharField(max_length=255, blank=True, null=True)
    names = models.CharField(max_length=255, blank=True, null=True)
    num_matches = models.IntegerField(blank=True, null=True)
    novel = models.CharField(max_length=255, blank=True, null=True)
    annotated = models.CharField(max_length=255, blank=True, null=True)
    corum = models.CharField(max_length=255, blank=True, null=True)
    reactome = models.CharField(max_length=255, blank=True, null=True)
    pindb = models.CharField(max_length=255, blank=True, null=True)
    hrpd = models.CharField(max_length=255, blank=True, null=True)
    go = models.CharField(max_length=255, blank=True, null=True)
    mend = models.CharField(max_length=255, blank=True, null=True)
    fly = models.CharField(max_length=255, blank=True, null=True)
    yeast = models.CharField(max_length=255, blank=True, null=True)
    tax = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'emili'

        
class Ensembl(models.Model):
    chrom = models.CharField(max_length=15, blank=True, null=True)
    authority = models.CharField(max_length=40, blank=True, null=True)
    gene_type = models.CharField(max_length=40, blank=True, null=True)
    scoord = models.IntegerField(blank=True, null=True)
    ecoord = models.IntegerField(blank=True, null=True)
    strand = models.CharField(max_length=1, blank=True, null=True)
    ensid = models.CharField(primary_key=True, max_length=40)
    gname = models.CharField(max_length=40, blank=True, null=True)
    geneid = models.CharField(max_length=40, blank=True, null=True)
    gtype = models.CharField(max_length=50, blank=True, null=True)
    taxid = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ensembl'


class Enshom(models.Model):
    eida = models.IntegerField(db_column='EIDA')  # Field name made lowercase.
    symbola = models.CharField(db_column='SYMBOLA', max_length=30, blank=True, null=True)  # Field name made lowercase.
    taxida = models.IntegerField(db_column='TAXIDA')  # Field name made lowercase.
    eidb = models.IntegerField(db_column='EIDB')  # Field name made lowercase.
    symbolb = models.CharField(db_column='SYMBOLB', max_length=30, blank=True, null=True)  # Field name made lowercase.
    taxidb = models.IntegerField(db_column='TAXIDB')  # Field name made lowercase.
    maptype = models.CharField(db_column='MAPTYPE', max_length=30, blank=True, null=True)  # Field name made lowercase.
    certainty = models.IntegerField(db_column='CERTAINTY', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'enshom'


class Entrez(models.Model):
    eid = models.IntegerField(db_column='EID', primary_key=True)  # Field name made lowercase.
    cdd = models.CharField(db_column='CDD', max_length=200, blank=True, null=True)  # Field name made lowercase.
    descr = models.CharField(db_column='DESCR', max_length=500, blank=True, null=True)  # Field name made lowercase.    
    external = models.CharField(db_column='EXTERNAL', max_length=200, blank=True, null=True)  # Field name made lowercase.
    location = models.CharField(db_column='LOCATION', max_length=50, blank=True, null=True)  # Field name made lowercase.
    peptide = models.TextField(db_column='PEPTIDE', blank=True, null=True)  # Field name made lowercase.
    pubmed = models.TextField(db_column='PUBMED', blank=True, null=True)  # Field name made lowercase.
    summary = models.CharField(db_column='SUMMARY', max_length=10000, blank=True, null=True)  # Field name made lowercase.
    swissprot = models.CharField(db_column='SWISSPROT', max_length=20, blank=True, null=True)  # Field name made lowercase.
    symbol = models.CharField(db_column='SYMBOL', max_length=200)  # Field name made lowercase.
    synonym = models.CharField(db_column='SYNONYM', max_length=5000, blank=True, null=True)  # Field name made lowercase.
    taxid = models.IntegerField(db_column='TAXID', blank=True, null=True)  # Field name made lowercase.
    trembl = models.CharField(db_column='TREMBL', max_length=20, blank=True, null=True)  # Field name made lowercase.
    genetype = models.CharField(db_column='GENETYPE', max_length=20, blank=True, null=True)  # Field name made lowercase.
    mrna = models.CharField(db_column='MRNA', max_length=10000, blank=True, null=True)  # Field name made lowercase.
    
    class Meta:
        managed = False
        db_table = 'entrez'


class EntrezGenes(models.Model):
    taxid = models.IntegerField()
    geneid = models.IntegerField(primary_key=True)
    symbol = models.CharField(max_length=30, blank=True, null=True)
    locustag = models.CharField(max_length=10, blank=True, null=True)
    synonyms = models.CharField(max_length=500, blank=True, null=True)
    dbxrefs = models.CharField(max_length=200, blank=True, null=True)
    chromosome = models.CharField(max_length=10, blank=True, null=True)
    map_location = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    type_of_gene = models.CharField(max_length=20, blank=True, null=True)
    offsymbol = models.CharField(max_length=30, blank=True, null=True)
    ofullname = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    other_designations = models.CharField(max_length=3000, blank=True, null=True)
    date_mod = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'entrez_genes'


class Gencode(models.Model):
    chrom = models.CharField(max_length=2)
    authority = models.CharField(max_length=40)
    gene_type = models.CharField(max_length=40)
    scoord = models.IntegerField(blank=True, null=True)
    ecoord = models.IntegerField(blank=True, null=True)
    strand = models.CharField(max_length=1, blank=True, null=True)
    ensid = models.CharField(max_length=40)
    gtype = models.CharField(max_length=50, blank=True, null=True)
    gstatus = models.CharField(max_length=10, blank=True, null=True)
    gname = models.CharField(max_length=40, blank=True, null=True)
    glevel = models.IntegerField(blank=True, null=True)
    taxid = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gencode'


class GeneCoords(models.Model):
    gid = models.AutoField(primary_key=True)
    taxid = models.IntegerField()
    geneid = models.IntegerField()
    chracc = models.CharField(max_length=15, blank=True, null=True)
    chrom = models.CharField(max_length=2, blank=True, null=True)
    chrgi = models.IntegerField(blank=True, null=True)
    start_pos = models.IntegerField(blank=True, null=True)
    end_pos = models.IntegerField(blank=True, null=True)
    orientation = models.CharField(max_length=1, blank=True, null=True)
    assembly = models.CharField(max_length=100, blank=True, null=True)
    symbol = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gene_coords'


class Hgnc(models.Model):
    hgnc_id = models.CharField(max_length=20, primary_key=True)
    symbol = models.CharField(max_length=40, blank=True, null=True)
    hgnc_name = models.CharField(max_length=500, blank=True, null=True)
    locus_group = models.CharField(max_length=20, blank=True, null=True)
    locus_type = models.CharField(max_length=40, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=40, blank=True, null=True)
    location_sortable = models.CharField(max_length=40, blank=True, null=True)
    alias_symbol = models.CharField(max_length=200, blank=True, null=True)
    alias_name = models.CharField(max_length=400, blank=True, null=True)
    prev_symbol = models.CharField(max_length=150, blank=True, null=True)
    prev_name = models.CharField(max_length=500, blank=True, null=True)
    gene_family = models.CharField(max_length=200, blank=True, null=True)
    gene_family_id = models.CharField(max_length=40, blank=True, null=True)
    date_approved_reserved = models.DateField(blank=True, null=True)
    date_symbol_changed = models.DateField(blank=True, null=True)
    date_name_changed = models.DateField(blank=True, null=True)
    date_modified = models.DateField(blank=True, null=True)
    entrez_id = models.IntegerField(blank=True, null=True)
    ensembl_gene_id = models.CharField(max_length=20, blank=True, null=True)
    vega_id = models.CharField(max_length=20, blank=True, null=True)
    ucsc_id = models.CharField(max_length=20, blank=True, null=True)
    ena = models.CharField(max_length=100, blank=True, null=True)
    refseq_accession = models.CharField(max_length=80, blank=True, null=True)
    ccds_id = models.CharField(max_length=300, blank=True, null=True)
    uniprot_ids = models.CharField(max_length=50, blank=True, null=True)
    pubmed_id = models.CharField(max_length=100, blank=True, null=True)
    mgd_id = models.CharField(max_length=1500, blank=True, null=True)
    rgd_id = models.CharField(max_length=50, blank=True, null=True)
    lsdb = models.CharField(max_length=800, blank=True, null=True)
    cosmic = models.CharField(max_length=20, blank=True, null=True)
    omim_id = models.CharField(max_length=20, blank=True, null=True)
    mirbase = models.CharField(max_length=20, blank=True, null=True)
    homeodb = models.CharField(max_length=20, blank=True, null=True)
    snornabase = models.CharField(max_length=20, blank=True, null=True)
    bioparadigms_slc = models.CharField(max_length=20, blank=True, null=True)
    orphanet = models.CharField(max_length=20, blank=True, null=True)
    pseudogene = models.CharField(max_length=20, blank=True, null=True)
    horde_id = models.CharField(max_length=20, blank=True, null=True)
    merops = models.CharField(max_length=20, blank=True, null=True)
    imgt = models.CharField(max_length=20, blank=True, null=True)
    iuphar = models.CharField(max_length=20, blank=True, null=True)
    kznf_gene_catalog = models.CharField(max_length=20, blank=True, null=True)
    mamit_trnadb = models.CharField(max_length=20, blank=True, null=True)
    cd = models.CharField(max_length=20, blank=True, null=True)
    lncrnadb = models.CharField(max_length=40, blank=True, null=True)
    enzyme_id = models.CharField(max_length=40, blank=True, null=True)
    intermediate_filament_db = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hgnc'


class Homologene(models.Model):
    hid = models.IntegerField(db_column='HID')  # Field name made lowercase.
    taxid = models.IntegerField(db_column='TAXID')  # Field name made lowercase.
    eid = models.IntegerField(db_column='EID')  # Field name made lowercase.
    symbol = models.CharField(db_column='SYMBOL', max_length=30, blank=True, null=True)  # Field name made lowercase.
    protgi = models.IntegerField(db_column='PROTGI', blank=True, null=True)  # Field name made lowercase.
    protacc = models.CharField(db_column='PROTACC', max_length=30, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'homologene'


class Interaction(models.Model):
    interid = models.CharField(db_column='INTERID', max_length=200, primary_key=True)  # Field name made lowercase.
    entreza = models.IntegerField(db_column='ENTREZA')  # Field name made lowercase.
    entrezb = models.IntegerField(db_column='ENTREZB')  # Field name made lowercase.
    symbola = models.CharField(db_column='SYMBOLA', max_length=50, blank=True, null=True)  # Field name made lowercase.
    symbolb = models.CharField(db_column='SYMBOLB', max_length=50, blank=True, null=True)  # Field name made lowercase.
    organisma = models.IntegerField(db_column='ORGANISMA', blank=True, null=True)  # Field name made lowercase.
    organismb = models.IntegerField(db_column='ORGANISMB', blank=True, null=True)  # Field name made lowercase.
    system = models.CharField(db_column='SYSTEM', max_length=300, blank=True, null=True)  # Field name made lowercase.
    systemtype = models.CharField(db_column='SYSTEMTYPE', max_length=20, blank=True, null=True)  # Field name made lowercase.
    throughput = models.CharField(db_column='THROUGHPUT', max_length=10, blank=True, null=True)  # Field name made lowercase.
    score = models.FloatField(db_column='SCORE', blank=True, null=True)  # Field name made lowercase.
    pmid = models.CharField(max_length=500, blank=True, null=True)  # Field name made lowercase.
    srcdb = models.CharField(db_column='SRCDB', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'interaction'


class Interactions(models.Model):
    bait = models.CharField(max_length=20, blank=True, null=True)
    prey = models.CharField(max_length=20, blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    pubmed = models.IntegerField(blank=True, null=True)
    dataset = models.CharField(max_length=20, blank=True, null=True)
    cond = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'interactions'


class ManualMapping(models.Model):
    symbol = models.CharField(max_length=100)
    entrezid = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'manual_mapping'

class Experiment(models.Model):
    uid = models.CharField(max_length=20, help_text='Unique id for the experiment: PJXnnn')
    name = models.CharField(max_length=50, help_text='Name for the experiment, e.g.: RalB S28N')
    exptype = models.CharField(max_length=5,
                               choices=(('apms', 'AP-MS'), ('apex2', 'APEX2'), ('tmt10', 'TMT10'), ('shotg', 'shotgun')),
                               help_text='The type of experiment, e.g.: AP-MS',
                               default='apms' ) 
    experimenter = models.CharField(max_length=50,
                                    blank=True,
                                    null=True,
                                    help_text='Who did the sample preparation?')
    lab = models.CharField(max_length=20,
                           choices=(('jackson', 'Jackson lab'), ('jackson/sage', 'Jackson/Sage labs'), ('sage', 'Sage lab'), ('attardi', 'Attardi lab'),
                                    ('fire', 'Fire lab'), ('einav', 'Einav lab'), ('carette', 'Carette lab'),
                                    ('gleeson', 'Gleeson lab'), ('arvin', 'Arvin lab'), ('bogyo', 'Bogyo lab'), ('cleary', 'Cleary lab'),
                                    ('cimprich', 'Cimprich lab'), ('lewis', 'Lewis lab'), ('chen', 'Chen lab'), ('poirier', 'Poirier lab'),
                                    ('sweet-cordero', 'Sweet-Cordero lab'), ('greenberg', 'Greenberg lab'), ('weis', 'Weis lab'), ('wernig', 'Wernig lab'),
                                    ('lenardo', 'Lenardo lab (NIH)')),
                           default='jackson',
                           help_text='Lab for which the experiment was conducted, e.g.:Jackson lab ')
    discard = models.NullBooleanField(blank = True, null = True,
                                  help_text = 'Is this a bad experiment?',
                                  choices = ((True, 'discard'), (False, 'keep')))

    def __str__(self):
        return '{} (id={})'.format(self.name, self.id)

    class Meta:
        managed = True
        ordering = ( 'lab', )
    
class ExperimentEdit(Experiment):

    class Meta:
        proxy = True


class ProtSample(models.Model):
    uid = models.CharField(max_length=20,
                           help_text='Unique id for the experiment: PJXnnn')
    name = models.CharField(max_length=50,
                             help_text='Name for the experiment, e.g.: RalB S28N')
    cell_line = models.CharField(max_length=50,
                                 help_text='cell line used for the experiment, e.g.: IMCD3')
    treatment = models.CharField(max_length=50,
                                 blank=True,
                                 null=True,
                                 help_text='experimental condition, e.g.: + doxorubicin')
    variant = models.CharField(max_length=50,
                               blank=True,
                               null=True,
                               help_text='Mutation/truncation ... in the bait, e.g.: mut (S17N - GDP)')
    genotype = models.CharField(max_length=50,
                                blank=True,
                                null=True,
                                help_text='Any genetic change in the cell line, e.g. RABL2Bdel')
    tag = models.CharField(max_length=5,
                           choices = (('nt', 'N-term'),('ct', 'C-term'),('lap1', 'N-term (LAP1)'), ('lap6', 'N-term (LAP6)'),
                                      ('lap7', 'C-term (LAP7)'),('ctv5', 'C-term (V5-TEV-S-tag)'), ('lap5', 'C-term (LAP5)'),
                                      ('lap3', 'N-term (LAP3)'), ('uk', 'unknown'), ('none', 'none')),
                           help_text='The tag, that is fused to the protein of interest, e.g.: N-term(LAP6)')
    tag_length = models.IntegerField(help_text='Length of the tag fused to the protein. This is only interesting for N-terminal fusions.',
                                     default = 0)
    bait_symbol = models.CharField(max_length=20,
                                   help_text='Gene symbol for the bait, e.g.: KRAS')
    eid = models.IntegerField( help_text='Entrez id for the gene', blank = True, null = True)
    lab = models.CharField(max_length=20,
                           choices=(('jackson', 'Jackson lab'), ('jackson/sage', 'Jackson/Sage labs'), ('sage', 'Sage lab'), ('attardi', 'Attardi lab'),
                                    ('fire', 'Fire lab'), ('einav', 'Einav lab'), ('carette', 'Carette lab'),
                                    ('gleeson', 'Gleeson lab'), ('arvin', 'Arvin lab'), ('bogyo', 'Bogyo lab'), ('cleary', 'Cleary lab'),
                                    ('cimprich', 'Cimprich lab'), ('lewis', 'Lewis lab'), ('chen', 'Chen lab'), ('poirier', 'Poirier lab'),
                                    ('sweet-cordero', 'Sweet-Cordero lab'), ('greenberg', 'Greenberg lab'), ('weis', 'Weis lab'), ('wernig', 'Wernig lab')),
                           default='jackson',
                           help_text='Lab for which the experiment was conducted, e.g.:Jackson lab ')
    exptype = models.CharField(max_length=5,
                               choices=(('apms', 'AP-MS'), ('apex2', 'APEX2'), ('tmt10', 'TMT10'), ('shotg', 'shotgun')),
                               help_text='The type of experiment, e.g.: AP-MS',
                               default='apms' )
    note = models.CharField(max_length=500,
                            blank=True,
                            null=True,
                            help_text="Any note(s) worth mentioning.")
    date = models.DateField(help_text='Date sample prep was finished.',
                            blank=True,
                            null=True,)
    taxid = models.IntegerField(blank=True, null=True, help_text='Taxid of organism of the cell line.', choices=((9606, 'human'),(10090, 'mouse'),(6239,'worm'),(10116,'rat')))
    experimenter = models.CharField(max_length=50,
                                    blank=True,
                                    null=True,
                                    help_text='Who did the sample preparation?')
    discard = models.NullBooleanField(blank = True, null = True,
                                  help_text = 'Is this a bad experiment?',
                                  choices = ((True, 'discard'), (False, 'keep')))
    fractions = models.IntegerField(blank=True, null=True, help_text='Number of fractions for this sample', default=8, editable=True)

    def get_absolute_url(self):
        """
        Returns the url to access a particular protsample instance.
        """
        return reverse('protsample-detail', args=[str(self.id)])

    class Meta:
        managed = True
        
    
class Psample(models.Model):
    expid = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, help_text='Name for the experiment, e.g.: RalB S28N')
    bait_symbol = models.CharField(max_length=20, help_text='Gene symbol for the bait, e.g.: KRAS')
    bait_eid = models.IntegerField( help_text='Entrez id for the gene', blank = True, null = True)
    bait_variant = models.CharField(max_length=50,
                               blank=True,
                               null=True,
                               help_text='Mutation/truncation ... in the bait, e.g.: mut (S17N - GDP)')
    cell_line = models.CharField(max_length=50,
                                 help_text='cell line used for the experiment, e.g.: IMCD3')
    genotype = models.CharField(max_length=50,
                                blank=True,
                                null=True,
                                help_text='Any genetic change in the cell line, e.g. RABL2Bdel')
    treatment = models.CharField(max_length=50,
                                 blank=True,
                                 null=True,
                                 help_text='experimental condition, e.g.: + doxorubicin')
    tag = models.CharField(max_length=5,
                           choices = (('nt', 'N-term'),('ct', 'C-term'),('lap1', 'N-term (LAP1)'), ('lap6', 'N-term (LAP6)'),
                                      ('lap7', 'C-term (LAP7)'),('ctv5', 'C-term (V5-TEV-S-tag)'), ('lap5', 'C-term (LAP5)'),
                                      ('lap3', 'N-term (LAP3)'), ('uk', 'unknown'), ('none', 'none')),
                           help_text='The tag, that is fused to the protein of interest, e.g.: N-term(LAP6)')
    tag_length = models.IntegerField(help_text='Length of the tag fused to the protein. This is only interesting for N-terminal fusions.',
                                     default = 0)
    taxid = models.IntegerField(blank=True, null=True, 
                                help_text='Taxid of organism of the cell line.', 
                                choices=((9606, 'human'),(10090, 'mouse'),(6239,'worm'),(10116,'rat')),
                                default = 9606)
    note = models.CharField(max_length=500,
                            blank=True,
                            null=True,
                            help_text="Any note(s) worth mentioning.")
    date = models.DateField(help_text='Date sample prep was finished.',
                            default=datetime.date.today,
                            blank=True,
                            null=True,)
    fractions = models.IntegerField(blank=True, null=True, help_text='Number of fractions for this sample', default=8, editable=True)
    
    class Meta:
        managed = True

    def __str__(self):
        return '{} (psid={}, expid={})'.format(self.name, self.id, self.expid)
        
        
class PsampleProxy(Psample):

    class Meta:
        proxy = True


class Mspec(models.Model):
    expid = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    name = models.CharField( max_length = 50,
                             help_text = 'Name for the mass spec run. E.g.: techrep 1')
    facility = models.CharField(max_length=5,
                                help_text='At which facility the MS was performed, e.g.: SUMS',
                                choices = (('lane', "Bill Lane facility"), ('sums', 'SUMS'), ('other', 'Other'), ('jl', 'Jackson Lab')),
                                default='sums',
                                null = True, blank = True)
    machine = models.CharField( max_length = 30,
                                choices = (('Thermo', 'Thermo'), ('timsTOF', 'timsTOF'), ('Velos', 'Velos'), ('Elite', 'Elite'), ('Fusion', 'Fusion')),
                                help_text = 'Machine that was used to run the mass spec.',
                                null = True, blank = True,
                                default = 'timsTOF')
    gradient = models.CharField(max_length=50,
                                help_text = 'LC gradient used for peptide separation.',
                                blank=True, null=True)
    method = models.CharField( max_length = 100,
                               help_text = 'Name of the method file containing params that wereused to generate the ms run. ',
                               blank=True, null=True)
    rundate = models.DateField(help_text='Date mass spec run was finished.',
                               default = datetime.date.today,
                               null=True, blank = True)
    rawfolder = models.CharField( max_length = 50,
                                  help_text = 'Folder where the raw data files can be found.',
                                  blank=True, null=True)
    
    def __str__(self):
        return '{} (expid={}, id={})'.format(self.name, self.expid, self.id)

    class Meta:
        managed = True


class MspecProxy(Mspec):
    class Meta:
        proxy = True


class Dproc(models.Model):
    msid = models.ForeignKey(Mspec, on_delete=models.CASCADE)
    expid = models.ForeignKey(Experiment, on_delete=models.CASCADE)    
    name = models.CharField( max_length = 50,
                             help_text = 'Name for the data processing step.',
                             blank=True, null=True)
    software = models.CharField( max_length = 30,
                                 choices = (('byonic', 'Byonic'), ('Other', 'Other')),
                                 help_text = 'Name of the software looking up the spectra.',
                                 default = 'byonic')
    paramfile = models.CharField( max_length = 50,
                                  help_text = 'Name of paramfile used.',
                                  blank=True, null=True)
    outfolder = models.CharField( max_length = 100,
                                  help_text = 'Name of folder where the output of the software is stored.',
                                  blank=True, null=True)
    rawfile = models.CharField(max_length=100,
                               null = True, blank = True,
                               help_text="Name of the 'rawfile' (protein level summary file) as given by the facility, e.g.: 20160718_NMooney_p53Extras_HeatMaps.xlsx")
    bgfile = models.CharField(max_length=100,
                              blank=True,
                              null=True,
                              help_text="Name of the 'background' (summary file of a pre-sample run) as given by the facility, e.g.: 160628_Blank_Pre_rerun_p53_plus.raw_20160711_Byonic_Mouse.xlsx")
    mrmsfile = models.CharField(max_length=50,
                                blank=True,
                                null=True,
                                help_text="Name of a converted (into text) of a 'rawfile', e.g.: IFT88_9606_RPE_RABL2B_WT.mrms")
    ff_folder = models.CharField(max_length=50,
                                 blank=True,
                                 null=True,                                 
                                 help_text="Name of folder where fraction files are stored.") 
    box_folder = models.CharField(max_length=50,
                                  blank=True,
                                  null=True,
                                  help_text="Name of folder in box account where data were uploaded by SUMS.") 
    date_back = models.DateField(help_text='Date the mass spec data were ready.',
                                 blank=True,
                                 null=True,
                                 default = datetime.date.today)
       
    def __str__(self):
        return '{} (id={})'.format(self.name, self.id)

    class Meta:
        managed = True
    
class DprocProxy(Dproc):
    class Meta:
        proxy = True

class Muts(models.Model):
    mutid = models.AutoField(primary_key=True)
    cancer_id = models.IntegerField()
    profile_id = models.IntegerField()
    alt_id = models.IntegerField()
    barcode_id = models.IntegerField()
    geneid = models.IntegerField()
    mut_status = models.CharField(max_length=20, blank=True, null=True)
    mut_type = models.CharField(max_length=50, blank=True, null=True)
    validation_status = models.CharField(max_length=20, blank=True, null=True)
    aa_change = models.CharField(max_length=50, blank=True, null=True)
    chrom = models.CharField(max_length=2, blank=True, null=True)
    start_pos = models.IntegerField(blank=True, null=True)
    end_pos = models.IntegerField(blank=True, null=True)
    ref_allele = models.CharField(max_length=200, blank=True, null=True)
    variant_allele = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'muts'


class Ncbiprots(models.Model):
    acc = models.CharField(db_column='ACC', max_length=20, primary_key=True)  # Field name made lowercase.
    gi = models.IntegerField(db_column='GI')  # Field name made lowercase.
    taxid = models.IntegerField(db_column='TAXID')  # Field name made lowercase.
    protname = models.CharField(db_column='PROTNAME', max_length=1000, blank=True, null=True)  # Field name made lowercase.    
    cds = models.CharField(db_column='CDS', max_length=200, blank=True, null=True)  # Field name made lowercase.
    eid = models.IntegerField(db_column='EID')  # Field name made lowercase.
    symbol = models.CharField(db_column='SYMBOL', max_length=50)  # Field name made lowercase.
    mrna = models.CharField(db_column='MRNA', max_length=5000, blank=True, null=True)  # Field name made lowercase.
    len = models.IntegerField(db_column='LEN', blank=True, null=True)  # Field name made lowercase.
    seq = models.TextField(db_column='SEQ', blank=True, null=True)  # Field name made lowercase.
    
    class Meta:
        managed = False
        db_table = 'ncbiprots'


class Numbers(models.Model):
    n = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'numbers'


class Orthology(models.Model):
    hgid = models.IntegerField()
    hs_symbol = models.CharField(max_length=40, blank=True, null=True)
    hs_geneid = models.IntegerField(blank=True, null=True)
    hgncid = models.CharField(max_length=20, blank=True, null=True)
    hs_spid = models.CharField(max_length=40, blank=True, null=True)
    mm_symbol = models.CharField(max_length=40, blank=True, null=True)
    mm_geneid = models.IntegerField(blank=True, null=True)
    mm_spid = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'orthology'

class Preproc(models.Model):
    dpid = models.ForeignKey(Dproc, on_delete=models.CASCADE)
    expid = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    special = models.CharField( max_length = 50,
                                help_text = 'Used to create the .i file; string to distinguish samples.',
                                blank=True, null=True)
    parser = models.CharField( max_length = 10,
                               help_text = 'Source file format - how to parse the data file.',
                               choices = (('lane', 'Lane'), ('sums', 'SUMS'), ('xml', 'XML'), ('laneExcel', 'LaneExcel')),
                               default = 'sums')
    comment = models.CharField( max_length = 200,
                                help_text = 'Any relevant comment related to this processing step.',
                                blank=True, null=True)
    display = models.NullBooleanField(help_text = 'Include this experiment in lookups?',
                                      choices = ((True, 'display'), (False, 'hide')),
                                      default = True)

    class Meta:
        managed = True
    
class PreprocProxy(Preproc):
    class Meta:
        proxy = True

class Preprocess(models.Model):
    rawfile = models.CharField( max_length = 100,
                                help_text = 'Excel file that contains protein level data',
                                blank=True, null=True)
    bait_symbol_eid = models.CharField( max_length = 30,
                                        help_text = 'bait symbol and entrez id (or 00): e.g. BBS4_585')
    taxid = models.IntegerField( help_text = 'NCBI taxonomy id for organism (of the cell line)',
                                 choices = ((9606, 9606), (10090, 10090)))
    special = models.CharField( max_length = 50,
                                help_text = 'Used to create the .i file; string to distinguish samples.',
                                blank=True, null=True)
    parser = models.CharField( max_length = 10,
                               help_text = 'Source file format - how to parse the data file.',
                               choices = (('lane', 'Lane'), ('sums', 'SUMS'), ('xml', 'XML'), ('laneExcel', 'LaneExcel')))
    bgfile = models.CharField( max_length = 100,
                              help_text = 'Pre-run (blank) file, if available.',
                              blank=True, null=True)
    mrmsfile = models.CharField( max_length = 50,
                                help_text = 'Name of text version of rawfile.',
                                blank=True, null=True)
    comment = models.CharField( max_length = 200,
                               help_text = 'Any relevant comment related to this processing step.',
                               blank=True, null=True)
    pjx = models.CharField( max_length = 20,
                            help_text = 'A PJXnnn id, that identifies the experiment.' )
    sampleid = models.IntegerField( help_text = 'This is the primary key value of the sample table. No foreign key relationship.',
                                    blank = True, null = True )
    
                    
class ProfBcs(models.Model):
    barcode_id = models.IntegerField()
    profile_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'prof_bcs'


class Profiles(models.Model):
    profile_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    descr = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'profiles'

class Fraction(models.Model):
    psid = models.ForeignKey(Psample, on_delete=models.CASCADE)
    expid = models.ForeignKey(Experiment, on_delete=models.CASCADE)    
    name = models.CharField( max_length = 50,
                             help_text = 'Name for the fraction. E.g.: band.1')
    digest = models.CharField( max_length = 30,
                               choices = (('trypsin', 'trypsin'), ('chymotrypsin', 'chymotrypsin')),
                               default = 'trypsin',
                               help_text = 'Enzyme used for digesting protein sample',
                               blank = True, null = True)
    method = models.CharField( max_length = 10,
                               help_text = 'Method used to generate fractions from sample. E.g." gel fractionation',
                               default = 'gelfrac',
                               editable = True,
                               choices = (('gelfrac', 'gel fractionation'), ('hplc', 'HPLC'), ('solution', 'solution')),
                               blank=True, null=True)
    deriv = models.CharField( max_length = 50,
                              default = 'baa',
                              help_text = 'Chemical used to derivatize peptides. E.g.: IAA',
                              choices = (('IAA', 'Iodo-Acetamide'), ('ClAA', 'Chloro-Acetamide'), ('acrylamide', 'Acrylamide')),
                              blank=True, null=True)
    mspec = models.ManyToManyField(Mspec, through='Frms')

    def __str__(self):
        return '{} (psid={}, id={})'.format(self.name, self.psid, self.id)

    class Meta:
        managed = True

class FractionProxy(Fraction):
    class Meta:
        proxy = True


class Refseq(models.Model):
    taxid = models.IntegerField(db_column='TAXID')  # Field name made lowercase.
    eid = models.IntegerField(db_column='EID')  # Field name made lowercase.
    status = models.CharField(db_column='STATUS', max_length=20, blank=True, null=True)  # Field name made lowercase.
    rna_acc = models.CharField(db_column='RNA_ACC', max_length=20, blank=True, null=True)  # Field name made lowercase.
    rna_version = models.IntegerField(db_column='RNA_VERSION', blank=True, null=True)  # Field name made lowercase.
    rna_gi = models.IntegerField(db_column='RNA_GI', blank=True, null=True)  # Field name made lowercase.
    prot_acc = models.CharField(db_column='PROT_ACC', max_length=20, blank=True, null=True)  # Field name made lowercase.
    prot_version = models.IntegerField(db_column='PROT_VERSION', blank=True, null=True)  # Field name made lowercase.
    prot_gi = models.IntegerField(db_column='PROT_GI', blank=True, null=True)  # Field name made lowercase.
    gennuc_acc = models.CharField(db_column='GENNUC_ACC', max_length=20)  # Field name made lowercase.
    gen_version = models.IntegerField(db_column='GEN_VERSION', blank=True, null=True)  # Field name made lowercase.
    gennuc_gi = models.IntegerField(db_column='GENNUC_GI')  # Field name made lowercase.
    scoord = models.IntegerField(db_column='SCOORD', blank=True, null=True)  # Field name made lowercase.
    ecoord = models.IntegerField(db_column='ECOORD', blank=True, null=True)  # Field name made lowercase.
    strand = models.CharField(db_column='STRAND', max_length=1, blank=True, null=True)  # Field name made lowercase.
    assembly = models.CharField(db_column='ASSEMBLY', max_length=50, blank=True, null=True)  # Field name made lowercase.
    pept_acc = models.CharField(db_column='PEPT_ACC', max_length=20, blank=True, null=True)  # Field name made lowercase.
    pept_gi = models.IntegerField(db_column='PEPT_GI', blank=True, null=True)  # Field name made lowercase.
    symbol = models.CharField(db_column='SYMBOL', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'refseq'

class Sample(models.Model):
    uid = models.CharField(max_length=20,
                           help_text='Unique id for the experiment: PJXnnn')
    label = models.CharField(max_length=50,
                             help_text='label for the experiment, e.g.: RalB S28N')
    cell_line = models.CharField(max_length=50,
                                 help_text='cell line used for the experiment, e.g.: IMCD3')
    cond = models.CharField(max_length=50,
                                 blank=True,
                                 null=True,
                                 help_text='experimental condition, e.g.: + doxorubicin')
    variant = models.CharField(max_length=50,
                               blank=True,
                               null=True,
                               help_text='Mutation/truncation ... in the bait, e.g.: mut (S17N - GDP)')
    tag = models.CharField(max_length=5,
                           choices = (('nt', 'N-term'),('ct', 'C-term'),('lap1', 'N-term (LAP1)'), ('lap6', 'N-term (LAP6)'),
                                      ('lap7', 'C-term (LAP7)'),('ctv5', 'C-term (V5-TEV-S-tag)'), ('lap5', 'C-term (LAP5)'),
                                      ('lap3', 'N-term (LAP3)'), ('uk', 'unknown'), ('none', 'none')),
                           help_text='The tag, that is fused to the protein of interest, e.g.: N-term(LAP6)')
    tag_length = models.IntegerField(help_text='Length of the tag fused to the protein. This is only interesting for N-terminal fusions.')
    facility = models.CharField(max_length=5,
                                help_text='At which facility the MS was performed, e.g.: SUMS',
                                choices = (('lane', "Bill Lane facility"), ('sums', 'SUMS'), ('other', 'Other')),
                                default='sums')
    bait_symbol = models.CharField(max_length=20,
                                   help_text='Gene symbol for the bait, e.g.: KRAS')
    eid = models.IntegerField( help_text='Entrez id for the gene', blank = True, null = True)
    rawfile = models.CharField(max_length=100,
                               help_text="Name of the 'rawfile' (protein level summary file) as given by the facility, e.g.: 20160718_NMooney_p53Extras_HeatMaps.xlsx")
    bgfile = models.CharField(max_length=100,
                              blank=True,
                              null=True,
                              help_text="Name of the 'background' (summary file of a pre-sample run) as given by the facility, e.g.: 160628_Blank_Pre_rerun_p53_plus.raw_20160711_Byonic_Mouse.xlsx")
    mrmsfile = models.CharField(max_length=50,
                                blank=True,
                                null=True,
                                help_text="Name of a converted (into text) of a 'rawfile', e.g.: IFT88_9606_RPE_RABL2B_WT.mrms")
    lab = models.CharField(max_length=20,
                           choices=(('jackson', 'Jackson lab'), ('jackson/sage', 'Jackson/Sage labs'), ('sage', 'Sage lab'), ('attardi', 'Attardi lab'),
                                    ('fire', 'Fire lab'), ('einav', 'Einav lab'), ('carette', 'Carette lab'),
                                    ('gleeson', 'Gleeson lab'), ('arvin', 'Arvin lab'), ('bogyo', 'Bogyo lab'), ('cleary', 'Cleary lab'),
                                    ('cimprich', 'Cimprich lab'), ('lewis', 'Lewis lab'), ('chen', 'Chen lab'), ('poirier', 'Poirier lab'),
                                    ('sweet-cordero', 'Sweet-Cordero lab'), ('greenberg', 'Greenberg lab'), ('weis', 'Weis lab'), ('wernig', 'Wernig lab')),
                           default='jackson',
                           help_text='Lab for which the experiment was conducted, e.g.:Jackson lab ')
    exptype = models.CharField(max_length=5,
                               choices=(('apms', 'AP-MS'), ('apex2', 'APEX2'), ('tmt10', 'TMT10'), ('shotg', 'shotgun')),
                               help_text='The type of experiment, e.g.: AP-MS',
                               default='apms' ) 
    note = models.CharField(max_length=500,
                            blank=True,
                            null=True,
                            help_text="Any note(s) worth mentioning.")
    raw_folder = models.CharField(max_length=100,
                                 blank=True,
                                 null=True,                                 
                                 help_text="Name of folder where raw datafiles are stored.")
    ff_folder = models.CharField(max_length=50,
                                 blank=True,
                                 null=True,                                 
                                 help_text="Name of folder where fraction files are stored.") 
    box_folder = models.CharField(max_length=50,
                                  blank=True,
                                  null=True,
                                  help_text="Name of folder in box account where data were uploaded by SUMS.") 
    date_back = models.DateField(help_text='Date the mass spec data were ready.',
                                 blank=True,
                                 null=True,)
    taxid = models.IntegerField(blank=True, null=True, help_text='Taxid of organism of the cell line.', choices=((9606, 'human'),(10090, 'mouse'),(6239,'worm'),(10116,'rat')))
    discard = models.NullBooleanField(blank = True, null = True,
                                  help_text = 'Is this a bad experiment?',
                                  choices = ((True, 'discard'), (False, 'keep')))
    display = models.NullBooleanField(blank = True, null = True,
                                  help_text = 'Include this experiment in lookups?',
                                  choices = ((True, 'display'), (False, 'hide')))
    
    
    def get_absolute_url(self):
        """
        Returns the url to access a particular sample instance.
        """
        return reverse('sample-detail', args=[str(self.id)])

    class Meta:
        managed = True

        
class Uniprot(models.Model):
    upacc = models.CharField(primary_key=True, max_length=20)
    upid = models.CharField(max_length=20, blank=True, null=True)
    eid = models.CharField(max_length=500, blank=True, null=True)
    refseqid = models.CharField(max_length=1000, blank=True, null=True)
    taxid = models.IntegerField(blank=True, null=True)
    omim = models.CharField(max_length=200, blank=True, null=True)
    pmid = models.CharField(max_length=5000, blank=True, null=True)
    ensid = models.CharField(max_length=500, blank=True, null=True)
    enspid = models.CharField(max_length=2000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'uniprot'


class Updet(models.Model):
    upacc = models.CharField(primary_key=True, max_length=20)
    upid = models.CharField(max_length=20, blank=True, null=True)
    srcdb = models.CharField(max_length=2)
    taxid = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    gname = models.CharField(max_length=50, blank=True, null=True)
    recname = models.CharField(max_length=200, blank=True, null=True)
    fullname = models.CharField(max_length=500, blank=True, null=True)
    shortname = models.CharField(max_length=200, blank=True, null=True)
    flags = models.CharField(max_length=20, blank=True, null=True)
    upaccs = models.CharField(max_length=1000, blank=True, null=True)
    eid = models.CharField(max_length=50, blank=True, null=True)
    refseqid = models.CharField(max_length=1000, blank=True, null=True)
    hgncid = models.CharField(max_length=50, blank=True, null=True)
    mgid = models.CharField(max_length=50, blank=True, null=True)
    domaindb = models.CharField(max_length=100, blank=True, null=True)
    domainid = models.CharField(max_length=1000, blank=True, null=True)
    domainname = models.CharField(max_length=2000, blank=True, null=True)
    seqinfo = models.IntegerField(blank=True, null=True)
    seq = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'updet'        

class Upfeats(models.Model):
    upacc   = models.CharField(primary_key=True, max_length=20)
    ftype   = models.CharField(max_length=20)
    fstart  = models.CharField(max_length=5)
    fstop   = models.CharField(max_length=5)
    feature = models.CharField(max_length=5000, blank=True, null=True)
    source  = models.CharField(max_length=2000, blank=True, null=True)
    extid   = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'upfeats'

class Upiso(models.Model):
    upacc = models.CharField(max_length=20)
    upid  = models.CharField(max_length=20, blank=True, null=True)
    isoid = models.CharField(primary_key=True, max_length=20)
    descr = models.CharField(max_length=500, blank=True, null=True)
    seq   = models.TextField(blank=True, null=True)    

    class Meta:
        managed = False
        db_table = 'upiso'
        
class Syns_view(models.Model):
    source = models.CharField(max_length=6)
    eid = models.CharField(max_length=20, blank=True, null=True)
    synonym = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'syns_view'
        
class Frms(models.Model):
    frid = models.ForeignKey(Fraction, on_delete=models.CASCADE)
    msid = models.ForeignKey(Mspec, on_delete=models.CASCADE)
    expid = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    name = models.CharField( max_length = 50,
                             help_text = 'Name for the fraction in the context of the ms run, if any. E.g.: Channel_126',
                             blank=True, null=True)

    class Meta:
        managed = True

class FrmsProxy(Frms):
    class Meta:
        proxy = True
    
    
class SummaryView(models.Model):
    id = models.IntegerField(primary_key = True)
    sid = models.IntegerField()
    dpid = models.IntegerField()
    uid = models.CharField(max_length=20)
    name  = models.CharField(max_length=50)
    special = models.CharField( max_length = 50, blank = True, null = True)
    experimenter = models.CharField( max_length = 50, blank = True, null = True)
    lab = models.CharField( max_length = 20)
    bait = models.CharField( max_length = 20)
    eid = models.IntegerField(blank = True, null = True)
    variant = models.CharField( max_length = 50, blank = True, null = True)
    cell_line = models.CharField( max_length = 50, blank = True, null = True)
    treatment = models.CharField( max_length = 50, blank = True, null = True)
    tag = models.CharField( max_length = 5, choices = (('nt', 'N-term'),('ct', 'C-term'),('lap1', 'N-term (LAP1)'), ('lap6', 'N-term (LAP6)'),
                                                       ('lap7', 'C-term (LAP7)'),('ctv5', 'C-term (V5-TEV-S-tag)'), ('lap5', 'C-term (LAP5)'),
                                                       ('lap3', 'N-term (LAP3)'), ('uk', 'unknown'), ('none', 'none')))
    tag_length = models.IntegerField()
    taxid  = models.IntegerField(blank = True, null = True)
    facility = models.CharField( max_length = 5, choices = (('lane', "Bill Lane facility"), ('sums', 'SUMS'), ('other', 'Other'), ('jl', 'Jackson Lab')), blank = True, null = True)
    software = models.CharField( max_length = 30, choices = (('byonic', 'Byonic'), ('Other', 'Other')))
    rawfile = models.CharField(max_length=100, blank = True, null = True)
    bgfile = models.CharField(max_length=100, blank = True, null = True)
    ff_folder = models.CharField(max_length=50, blank = True, null = True)
    date_back = models.DateField(blank = True, null = True) 
    discard = models.NullBooleanField(blank = True, null = True, choices = ((True, 'discard'), (False, 'keep')))
    display = models.NullBooleanField(blank = True, null = True, choices = ((True, 'display'), (False, 'hide')))

    class Meta:
        managed = False
        db_table = 'summary_view'
