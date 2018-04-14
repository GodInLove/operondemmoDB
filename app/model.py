# coding:utf8
from app import app
from flask_mongoengine import MongoEngine
from werkzeug.security import check_password_hash

from PyOpdb.scripts import generate_simple_gff, get_gene_from_file, get_operon_from_file

db = MongoEngine(app)


class Admin(db.Document):
    email = db.EmailField()
    admin_id = db.StringField(max_length=50)
    password = db.StringField()

    def __repr__(self):
        return "Admin.email:%s\nAdmin.id:%s" % self.email, self.admin_id

    def check_pwd(self, password):
        return check_password_hash(self.password, password)


class Gene(db.EmbeddedDocument):
    locus_tag = db.StringField()
    start = db.IntField()
    stop = db.IntField()
    strand = db.StringField()

    def __repr__(self):
        return "Gene:%s" % self.locus_tag


class GeneTpm(db.EmbeddedDocument):
    locus_tag = db.StringField()


class TU(db.EmbeddedDocument):
    genes = db.EmbeddedDocumentListField(GeneTpm)


class Condition(db.EmbeddedDocument):
    reps = db.ListField(db.StringField())


class SrrTask(db.Document):
    _id = db.StringField(primary_key=True)
    srr_nums = db.EmbeddedDocumentListField(Condition)
    kegg_id = db.StringField()
    browse_link = db.URLField()
    operon_path = db.StringField()
    operon = db.EmbeddedDocumentListField(TU)
    bw_path = db.StringField()
    method = db.StringField()
    add_time = db.DateTimeField()

    def __repr__(self):
        return "SRR:%s" % self.srr_id

    def get_srr_nums(self, data):
        for con in data:
            condition = Condition()
            condition.reps = con
            self.srr_nums.append(condition)

    def get_operons_from_file(self, operon_file):
        data_list = get_operon_from_file(operon_file)
        for data in data_list:
            tu = TU()
            for each in data:
                gene_tpm = GeneTpm()
                gene_tpm.locus_tag = each
                tu.genes.append(gene_tpm)
            self.operon.append(tu)


class TaskId(db.Document):
    _id = db.ObjectIdField()
    srr_id = db.StringField(required=True)
    email = db.EmailField(required=True)
    task_time = db.DateTimeField()


class Specie(db.Document):
    kegg_id = db.StringField(primary_key=True)
    specie_name = db.StringField()
    add_time = db.DateTimeField()
    genes = db.EmbeddedDocumentListField(Gene)
    gff_path = db.StringField()

    def get_genes_from_file(self, gff_file):
        simple_gff = generate_simple_gff(gff_file)
        data_list = get_gene_from_file(simple_gff)
        for each in data_list:
            gene = Gene()
            gene.locus_tag = each["locus_tag"]
            gene.start = each["start"]
            gene.stop = each["stop"]
            gene.strand = each["strand"]
            self.genes.append(gene)
