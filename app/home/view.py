# coding:utf8
from datetime import datetime

import os

from flask_mail import Message
from werkzeug.utils import secure_filename

from app.home.operon import operon_predict
from . import home
from flask import render_template, redirect, url_for, flash, request, send_from_directory, abort
from app.home.forms import SubmitForm, ContactForm, DatabaseForm
from app.model import SrrTask, TaskId, Specie
from concurrent.futures import ThreadPoolExecutor
from app import path, sender, mail, app
import uuid

executor = ThreadPoolExecutor(1)


@home.route("/", methods=['GET', 'POST'])
def index():
    submit_form = SubmitForm()
    if submit_form.condition_add.data:
        submit_form.condition.append_entry()
        return render_template("home/index.html", form=submit_form)
    i_iter = 0
    for con in submit_form.condition.entries:
        if con.condition_del.data:
            submit_form.condition.entries.pop(i_iter)
            return render_template("home/index.html", form=submit_form)
        if con.repeat_add.data:
            submit_form.condition.entries[i_iter].repeat.append_entry()
            return render_template("home/index.html", form=submit_form)
        j_iter = 0
        for rep in con.repeat.entries:
            if rep.repeat_del.data:
                submit_form.condition.entries[i_iter].repeat.entries.pop(j_iter)
                return render_template("home/index.html", form=submit_form)
            j_iter = j_iter + 1
        i_iter = i_iter + 1
    auto = ""
    if submit_form.kegg_auto.data:
        auto = "y"
    if submit_form.kegg_not_auto.data:
        auto = "n"
    if submit_form.validate_on_submit():
        data = submit_form.data
        srr_list = []
        all_srr = []
        for con in data["condition"]:
            srr_list.append([])
            for each in con["repeat"]:
                srr_list[-1].append(each['srr'])
                all_srr.append(each['srr'])
        all_srr = sorted(all_srr)
        srr_id = "-".join(all_srr)
        data_count = SrrTask.objects(_id=srr_id).count()
        if data_count == 1:
            return redirect(url_for("home.srr_id", _id=srr_id))

        new_task_id = TaskId(task_id=str(uuid.uuid1()), srr_id=srr_id, email=data["email"], task_time=datetime.now())
        new_task_id.save()

        if submit_form.gff_file.data is not None:
            gff = submit_form.gff_file.data
            gff_filename = secure_filename(gff.filename)
            gff_path = os.path.join(path, data["kegg_id"], gff_filename)
            if not os.path.exists(path):
                os.system("mkdir " + path)
            if not os.path.exists(os.path.join(path, data["kegg_id"])):
                os.system("mkdir " + os.path.join(path, data["kegg_id"]))
            gff.save(gff_path)
            fna = submit_form.fna_file.data
            fna_filename = secure_filename(fna.filename)
            fna_path = os.path.join(path, data["kegg_id"], fna_filename)
            if not os.path.exists(os.path.join(path, data["kegg_id"])):
                os.system("mkdir " + os.path.join(path, data["kegg_id"]))
            fna.save(fna_path)

        kegg_id = data["kegg_id"]
        soft = data["software_select"]
        method = data["method_select"]
        corr = data["correlation_select"]

        executor.submit(operon_predict, srr_list, kegg_id, soft, method, corr, srr_id)

        return redirect(url_for("home.wait"))

    return render_template("home/index.html", form=submit_form, auto=auto)


@home.route("/demonstration/")
def demonstration():
    return render_template("home/demonstration.html")


@home.route("/database/gene/<_id>/", methods=['GET'])
@home.route("/database/gene/<_id>/<int:page>/", methods=['GET'])
def specie_gene(_id=None, page=None):
    if page is None:
        page = 1
    specie_query = Specie.objects(kegg_id=_id).first()
    page_data = specie_query.paginate_field("genes", page=page, per_page=50)
    return render_template("home/specie_gene.html", page_data=page_data)


@home.route("/database/operon/<_id>/", methods=['GET'])
@home.route("/database/operon/<_id>/<int:page>/", methods=['GET'])
def srr_task_operon(_id=None, page=None):
    if page is None:
        page = 1
    srr_task_query = SrrTask.objects(_id=_id).first()
    page_data = srr_task_query.paginate_field("operon", page=page, per_page=50)
    return render_template("home/srr_task_operon.html", page_data=page_data)


@home.route("/database/", methods=["GET", "POST"])
def database():
    database_form = DatabaseForm()
    if database_form.validate_on_submit():
        data = database_form.data
        query = data["query"]
        res = []
        each = {}
        if data["select"] == "specie":
            query_data = Specie.objects(kegg_id=query)
            for item in query_data:
                each["kegg_id"] = item.kegg_id
                each["specie_name"] = item.specie_name
                res.append(each)
            return render_template("home/database.html", form=database_form, res=res, type="specie")
        else:
            query_data = SrrTask.objects(_id__icontains=query)
            for item in query_data:
                each["_id"] = item._id
                each["kegg_id"] = item.kegg_id
                each["method"] = item.method
                res.append(each)
            query_data2 = SrrTask.objects(kegg_id=query)
            for item in query_data2:
                each["_id"] = item._id
                each["kegg_id"] = item.kegg_id
                each["method"] = item.method
                each["browse_link"] = item.browse_link
                res.append(each)
            return render_template("home/database.html", form=database_form, res=res, type="srr_task")
    return render_template("home/database.html", form=database_form, res=None, type=None)


@home.route("/about/")
def about():
    return render_template("home/about.html")


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


@home.route("/contact/", methods=["GET", "POST"])
def contact():
    contact_form = ContactForm()
    if contact_form.validate_on_submit():
        data = contact_form.data
        msg = Message("OperondemmoDB Contact", sender=sender, recipients=["ttttttliu@163.com"])
        msg.body = "email:" + data["email"] + "\ncontent:" + data["text"]
        executor.submit(send_async_email, app, msg)
        # mail.send(msg)
        flash("send OK", "ok")
        return redirect(url_for("home.contact"))
    return render_template("home/contact.html", form=contact_form)


@home.route("/wait/")
def wait():
    return render_template("home/wait.html")


@home.route("/srr_id/<_id>/")
def srr_id(_id):
    srr_task_query = SrrTask.objects.get_or_404(_id=_id)
    each = {"_id": srr_task_query._id, "kegg_id": srr_task_query.kegg_id, "method": srr_task_query.method,
            "operon": srr_task_query.operon_path, "jbrowse": srr_task_query.browse_link}
    print(each)
    return render_template("home/task.html", each=each)


@home.route("/task/<_id>/")
def task_id(_id):
    task_query = TaskId.objects(task_id=_id).first()
    srr_id_query = task_query.srr_id
    srr_task_query = SrrTask.objects.get_or_404(_id=srr_id_query)
    each = {"_id": srr_task_query._id, "kegg_id": srr_task_query.kegg_id, "method": srr_task_query.method,
            "operon": srr_task_query.operon_path, "jbrowse": srr_task_query.browse_link}
    return render_template("home/task.html", each=each)


@home.route("/instance/<_id>/operon/operon.txt")
def download(_id):
    download_path = os.path.join(path, _id, "operon")
    if request.method == "GET":
        if os.path.isfile(os.path.join(download_path, "operon.txt")):
            return send_from_directory(download_path, "operon.txt", as_attachment=True)
        abort(404)
