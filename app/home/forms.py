# coding:utf8
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, RadioField, SubmitField, FieldList, FormField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email


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


class SubmitForm(FlaskForm):
    kegg_id = StringField(
        label="kegg id",
        description="kegg id",
        validators=[
            DataRequired("please enter the kegg id !")
        ],
        render_kw={
            "placeholder": "please enter the kegg id",
        }
    )
    kegg_auto = SubmitField(
        label="auto download",
        render_kw={
            "class": "btn btn-info icon fa-plus",
        }
    )
    kegg_not_auto = SubmitField(
        label="upload",
        render_kw={
            "class": "btn btn-info icon fa-plus",
        }
    )
    gff_file = FileField(
        label="gff file",
        validators=[
            FileAllowed(['gff', 'gff3'], "GFF ONLY !")
        ],
        render_kw={
            "class": "btn btn-lg btn-primary btn-block",
        }
    )
    fna_file = FileField(
        label="fna file",
        validators=[
            FileAllowed(['fna', 'fa', 'faa', 'fasta'], "FASTA ONLY !")
        ],
        render_kw={
            "class": "btn btn-lg btn-primary btn-block",
        }
    )
    condition = FieldList(
        FormField(ConditionForm),
        label="Input Srr ID",
        min_entries=1,
    )
    condition_add = SubmitField(
        label="Condition +",
        render_kw={
            "class": "btn btn-info icon fa-plus",
        }
    )
    email = StringField(
        label="email",
        validators=[
            DataRequired("please enter the email !"),
            Email("the format is wrong !")
        ],
        description="email",
    )
    software_select = SelectField(
        label="software",
        choices=[
            ("rockhopper", "rockhopper"),
            ("operondemmo", "operondemmo"),
        ]
    )
    method_select = SelectField(
        label="method",
        choices=[
            ("GD", "Gamma Domain"),
            ("NB", "Naive Bayes"),
        ]
    )
    correlation_select = SelectField(
        label="correlation",
        choices=[
            ("c_i_j", "c_i_j"),
            ("spearman", "spearman"),
            ("pearson", "pearson")
        ]
    )
    submit = SubmitField(
        label="submit",
        render_kw={
            "class": "btn btn-lg btn-primary btn-block",
        }
    )


class MethodForm(FlaskForm):
    rockhopper = SubmitField(
        label="rockhopper",
        render_kw={
            "class": "btn btn-info icon fa-plus",
        }
    )
    operondemmo = SubmitField(
        label="operondemmo",
        render_kw={
            "class": "btn btn-info icon fa-plus",
        }
    )


class ContactForm(FlaskForm):
    email = StringField(
        label="email",
        validators=[
            DataRequired("please enter the email !"),
            Email("the format is wrong !")
        ],
        description="email",
    )
    text = TextAreaField(
        label="content",
        validators=[
            DataRequired("please enter the message !"),
        ]
    )
    submit = SubmitField(
        label="submit",
        render_kw={
            "class": "btn btn-lg btn-primary btn-block",
        }
    )


class DatabaseForm(FlaskForm):
    select = SelectField(
        label="select",
        choices=[
            ("specie", "specie"),
            ("srr_task", "srr_task"),
        ]
    )
    query = StringField(
        label="query",
        validators=[
            DataRequired("please enter the query !"),
        ]
    )
    submit = SubmitField(
        label="submit",
        render_kw={
            "class": "btn btn-lg btn-primary btn-block",
        }
    )