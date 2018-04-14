# coding:utf8
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, FieldList, FormField
from wtforms.validators import DataRequired, ValidationError, URL, Email
from app.model import Admin, TaskId, Specie


class LoginForm(FlaskForm):
    admin_id = StringField(
        label='admin',
        validators=[
            DataRequired("please enter your admin id !"),
        ],
        description="admin id",
        render_kw={
            "placeholder": "admin",
            "class": "form-control",
        }
    )
    password = PasswordField(
        label="password",
        validators=[
            DataRequired("please enter your password !")
        ],
        description="password",
        render_kw={
            "placeholder": "password",
            "class": "form-control",
        }
    )
    submit = SubmitField(
        label="Login",
        render_kw={
            "class": "btn btn-lg btn-primary btn-block",
        }
    )

    def validate_admin_id(self, field):
        admin_id = field.data
        admins_count = Admin.objects(admin_id=admin_id).count()
        if admins_count == 0:
            raise ValidationError("this admin is not exist !")


class SpecieForm(FlaskForm):
    kegg_id = StringField(
        label="kegg id",
        validators=[
            DataRequired("please enter the kegg id of the specie !")
        ],
        description="kegg id",
        render_kw={
            "placeholder": "please enter the kegg id",
        }
    )
    specie_name = StringField(
        label="specie name",
        validators=[
            DataRequired("please enter the name of the specie !")
        ],
        description="specie name",
        render_kw={
            "placeholder": "please enter the name",
        }
    )
    save_path = StringField(
        label="save path",
        validators=[
            DataRequired("please enter the save path in server !")
        ],
        description="save path",
        render_kw={
            "placeholder": "/home/my/JBrowse",
        }
    )
    gff_file = FileField(
        label="gff file",
        validators=[
            FileRequired("please select a file !"),
            FileAllowed(['gff', 'gff3'], "GFF ONLY !")
        ],
        render_kw={
            "class": "btn btn-lg btn-primary btn-block",
        }
    )
    submit = SubmitField(
        label="submit",
        render_kw={
            "class": "btn btn-lg btn-primary btn-block",
        }
    )

    def validate_kegg_id(self, field):
        kegg_id = field.data
        kegg_id_count = Specie.objects(kegg_id=kegg_id).count()
        if kegg_id_count > 0:
            raise ValidationError("WRONG! This specie is already exist !")


class TUGeneForm(FlaskForm):
    locus_tag = StringField(
        label="locus tag",
        validators=[
            DataRequired("please enter the kegg id of the specie !")
        ],
        description="locus tag"
    )
    tpm = StringField(
        label="tpm",
        validators=[
            DataRequired("please enter the tpm !")
        ],
        description="tpm"
    )


class TUForm(FlaskForm):
    tus = FieldList(FormField(TUGeneForm))


class RepForm(FlaskForm):
    srr = StringField(
        label="srr",
        validators=[
            DataRequired("please enter the rep !")
        ],
        render_kw={
            "class": "text",
            "placeholder": "SRRXXXXX",
        }
    )
    repeat_del = SubmitField(
        label="Repeat -",
        render_kw={
            "class": "btn btn-danger icon fa-minus",
        }
    )

    def __init__(self, csrf_enabled=False, *args, **kwargs):
        super(RepForm, self).__init__(csrf_enabled=False, *args, **kwargs)


class ConditionForm(FlaskForm):
    repeat = FieldList(
        FormField(RepForm),
        min_entries=1,
    )
    condition_del = SubmitField(
        label="Condition -",
        render_kw={
            "class": "btn btn-danger icon fa-minus",
        }
    )
    repeat_add = SubmitField(
        label="Repeat +",
        render_kw={
            "class": "btn btn-info icon fa-plus",
        }
    )

    def __init__(self, csrf_enabled=False, *args, **kwargs):
        super(ConditionForm, self).__init__(csrf_enabled=False, *args, **kwargs)


class SrrTaskForm(FlaskForm):
    condition = FieldList(
        FormField(ConditionForm),
        label="Input Srr ID",
    )
    condition_add = SubmitField(
        label="Condition +",
        render_kw={
            "class": "btn btn-info icon fa-plus",
        }
    )
    kegg_id = StringField(
        label="kegg id",
        validators=[
            DataRequired("please enter the kegg id of the specie !")
        ],
        description="kegg id",
    )
    browse_link = StringField(
        label="browse link",
        validators=[
            DataRequired("please enter the browse link !"),
            URL(message="the format is wrong !")
        ],
        description="browse link",
        render_kw={
            "placeholder": "http://xxx.xxx.xxx",
        }
    )
    operon_path = StringField(
        label="operon path",
        validators=[
            DataRequired("please enter the operon_path !")
        ],
        description="bw_path",
    )
    operon_file = FileField(
        label="operon file",
        validators=[
            FileRequired("please select a file !"),
            FileAllowed(["txt", "out"], "TXT ONLY !")
        ],
        render_kw={
            "class": "btn btn-lg btn-primary btn-block",
        }
    )
    bw_path = StringField(
        label="bw_path",
        validators=[
            DataRequired("please enter the bw_path !")
        ],
        description="bw_path",
    )
    method = SelectField(
        label="method",
        choices=[
            ("GD", "Gamma Domain"),
            ("NB", "Naive Bayes"),
        ]
    )
    submit = SubmitField(
        label="submit",
        render_kw={
            "class": "btn btn-lg btn-primary btn-block",
        }
    )


class GeneForm(FlaskForm):
    locus_tag = StringField(
        label="locus_tag",
    )
    start = IntegerField(

    )
    stop = IntegerField(

    )
    strand = StringField(

    )
    tpm = StringField(

    )


class TaskIDForm(FlaskForm):
    srr_id = StringField(
        label="srr id",
        validators=[
            DataRequired("please enter the srr id !")
        ],
        description="srr id",
    )
    email = StringField(
        label="email",
        validators=[
            DataRequired("please enter the email !"),
            Email("the format is wrong !")
        ],
        description="email",
    )
    submit = SubmitField(
        label="submit",
        render_kw={
            "class": "btn btn-lg btn-primary btn-block",
        }
    )

    def validate_srr_id(self, field):
        data = field.data
        data_count = TaskId.objects(srr_id=data).count()
        if data_count > 0:
            raise ValidationError("the srr id is already exist !")
