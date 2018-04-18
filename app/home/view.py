# coding:utf8
from datetime import datetime

import os
from werkzeug.utils import secure_filename

from app.home.operon import operon_predict
from . import home
from flask import render_template, redirect, url_for
from app.home.forms import SubmitForm
from app.model import SrrTask, TaskId
from concurrent.futures import ThreadPoolExecutor
from app import path

executor = ThreadPoolExecutor(1)


@home.route("/", methods=['GET', 'POST'])
def index(_var=None):
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

        new_task_id = TaskId(srr_id=srr_id, email=data["email"], task_time=datetime.now())
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


@home.route("/database/")
def database():
    return render_template("home/database.html")


@home.route("/about/")
def about():
    return render_template("home/about.html")


@home.route("/contact/")
def contact():
    return render_template("home/contact.html")


@home.route("/wait/")
def wait():
    return render_template("home/wait.html")


@home.route("/srr_id/<_id>")
def srr_id(_id):
    srr_task_query = SrrTask.objects.get_or_404(_id=_id)
    link = srr_task_query.browse_link
    return redirect(link)