# coding:utf8
import os

from flask_mongoengine import Pagination
from . import admin
from flask import render_template, redirect, url_for, flash, session, request
from app.admin.forms import LoginForm, SpecieForm, SrrTaskForm, TaskIDForm
from app.model import Admin, Specie, SrrTask, TaskId
from functools import wraps
from datetime import datetime
from werkzeug.utils import secure_filename
from app import path


def admin_login_req(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if "admin_id" not in session:
            return redirect(url_for("admin.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_func


# index
@admin.route("/")
@admin_login_req
def index():
    return render_template("admin/index.html")


# login
@admin.route("/login/", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        admin_query = Admin.objects(admin_id=data["admin_id"]).first()
        if not admin_query.check_pwd(data["password"]):
            flash("the password is incorrect !")
            return redirect(url_for("admin.login"))
        session["admin_id"] = data["admin_id"]
        return redirect(request.args.get("next") or url_for("admin.index"))
    return render_template("admin/login.html", form=form)


@admin.route("/login_out/")
@admin_login_req
def login_out():
    session.pop("admin_id", None)
    return redirect(url_for("admin.login"))


@admin.route("/specie/gene/<_id>/", methods=['GET'])
@admin.route("/specie/gene/<_id>/<int:page>/", methods=['GET'])
@admin_login_req
def specie_gene(_id=None, page=None):
    if page is None:
        page = 1
    specie_query = Specie.objects(kegg_id=_id).first()
    page_data = specie_query.paginate_field("genes", page=page, per_page=50)
    return render_template("admin/specie_gene.html", page_data=page_data)


@admin.route("/specie/")
@admin.route("/specie/<int:page>/", methods=['GET'])
@admin_login_req
def specie(page=None):
    if page is None:
        page = 1
    page_data = Specie.objects().paginate(page=page, per_page=10)
    return render_template("admin/specie.html", page_data=page_data)


@admin.route("/specie/add/", methods=['GET', 'POST'])
@admin_login_req
def specie_add():
    specie_form = SpecieForm()
    if specie_form.validate_on_submit():
        data = specie_form.data
        f = specie_form.gff_file.data
        filename = secure_filename(f.filename)
        save_path = os.path.join(data["save_path"], "gff_file", filename)
        if not os.path.exists(path):
            os.system("mkdir " + path)
        if not os.path.exists(os.path.join(path, "gff_file")):
            os.system("mkdir " + os.path.join(path, "gff_file"))
        f.save(save_path)
        new_specie = Specie(kegg_id=data["kegg_id"], specie_name=data["specie_name"], gff_path=data["save_path"],
                            add_time=datetime.now())
        new_specie.get_genes_from_file(save_path)
        new_specie.save()
        flash("this specie is added !", "ok")
        return redirect(url_for("admin.specie_add"))
    return render_template("admin/specie_add.html", form=specie_form)


@admin.route("/specie/edit/<_id>", methods=['GET', 'POST'])
@admin_login_req
def specie_edit(_id=None):
    specie_form = SpecieForm()
    specie_query = Specie.objects.get_or_404(kegg_id=_id)
    if specie_form.validate_on_submit():
        data = specie_form.data
        old_path = specie_query.gff_path
        Specie.objects(kegg_id=_id).update_one(set__specie_name=data["specie_name"])
        Specie.objects(kegg_id=_id).update_one(set__gff_path=data["save_path"])
        if not os.path.exists(data["save_path"]):
            os.makedirs(data["save_path"])
        os.system("mv " + old_path + " " + data["save_path"])
        Specie.objects(kegg_id=_id).update_one(set__add_time=datetime.now())
        flash("edit done !", "ok")
        return redirect(url_for("admin.specie_edit", _id=_id))
    return render_template("admin/specie_edit.html", form=specie_form, specie=specie_query)


@admin.route("/specie/del/<_id>/", methods=['GET'])
@admin_login_req
def specie_del(_id=None):
    Specie.objects(kegg_id=_id).delete()
    flash("delete it done !", "ok")
    return redirect(url_for("admin.specie"))


# srr task
@admin.route("/srr_task/")
@admin.route("/srr_task/<int:page>/", methods=['GET'])
@admin_login_req
def srr_task(page=None):
    if page is None:
        page = 1
    page_data = SrrTask.objects().paginate(page=page, per_page=10)
    return render_template("admin/srr_task.html", page_data=page_data)


@admin.route("/srr_task/nums/<_id>/", methods=['GET'])
@admin.route("/specie/nums/<_id>/<int:page>/", methods=['GET'])
@admin_login_req
def srr_task_nums(_id=None, page=None):
    if page is None:
        page = 1
    srr_task_query = SrrTask.objects(_id=_id).first()
    page_data = srr_task_query.paginate_field("srr_nums", page=page, per_page=50)
    return render_template("admin/srr_task_nums.html", page_data=page_data)


@admin.route("/srr_task/operon/<_id>/", methods=['GET'])
@admin.route("/specie/operon/<_id>/<int:page>/", methods=['GET'])
@admin_login_req
def srr_task_operon(_id=None, page=None):
    if page is None:
        page = 1
    srr_task_query = SrrTask.objects(_id=_id).first()
    page_data = srr_task_query.paginate_field("operon", page=page, per_page=50)
    return render_template("admin/srr_task_operon.html", page_data=page_data)


@admin.route("/srr_task/add/", methods=['GET', 'POST'])
@admin_login_req
def srr_task_add():
    srr_task_form = SrrTaskForm()
    validate = True
    if srr_task_form.condition_add.data:
        srr_task_form.condition.append_entry()
        return render_template("admin/srr_task_add.html", form=srr_task_form)
    i_iter = 0
    for con in srr_task_form.condition.entries:
        if con.condition_del.data:
            srr_task_form.condition.entries.pop(i_iter)
            return render_template("admin/srr_task_add.html", form=srr_task_form)
        if con.repeat_add.data:
            srr_task_form.condition.entries[i_iter].repeat.append_entry()
            return render_template("admin/srr_task_add.html", form=srr_task_form)
        j_iter = 0
        for rep in con.repeat.entries:
            if rep.repeat_del.data:
                srr_task_form.condition.entries[i_iter].repeat.entries.pop(j_iter)
                return render_template("admin/srr_task_add.html", form=srr_task_form)
            j_iter = j_iter + 1
        i_iter = i_iter + 1
    if validate:
        if srr_task_form.validate_on_submit():
            data = srr_task_form.data
            all_srr = []
            srr_list = []
            for con in data["condition"]:
                srr_list.append([])
                for each in con["repeat"]:
                    srr_list[-1].append(each['srr'])
                    all_srr.append(each['srr'])
            all_srr = sorted(all_srr)
            srr_id = "-".join(all_srr)
            data_count = SrrTask.objects(_id=srr_id).count()
            if data_count == 1:
                flash("this srr_id is already exist !", "err")
                return redirect(url_for("admin.srr_task_add"))
            new_srr_task = SrrTask(_id=srr_id, kegg_id=data["kegg_id"], browse_link=data["browse_link"],
                                   operon_path=data["operon_path"], bw_path=data["bw_path"], method=data["method"],
                                   add_time=datetime.now())
            new_srr_task.get_srr_nums(srr_list)
            f = srr_task_form.operon_file.data
            filename = secure_filename(f.filename)
            save_path = os.path.join(data["operon_path"], "operon_file", filename)
            if not os.path.exists(path):
                os.system("mkdir " + path)
            if not os.path.exists(os.path.join(path, "operon_file")):
                os.system("mkdir " + os.path.join(path, "operon_file"))
            f.save(save_path)
            new_srr_task.get_operons_from_file(save_path)
            new_srr_task.save()
            flash("this srr_task is added !", "ok")
            return redirect(url_for("admin.srr_task_add"))
    return render_template("admin/srr_task_add.html", form=srr_task_form)


@admin.route("/srr_task/edit/<_id>", methods=['GET', 'POST'])
@admin_login_req
def srr_task_edit(_id=None):
    srr_task_form = SrrTaskForm()
    srr_task_query = SrrTask.objects.get_or_404(_id=_id)
    old_bw_path = srr_task_query.bw_path
    old_operon_path = srr_task_query.operon_path
    if srr_task_form.validate_on_submit():
        data = srr_task_form.data
        SrrTask.objects(_id=_id).update_one(set__kegg_id=data["kegg_id"])
        SrrTask.objects(_id=_id).update_one(set__browse_link=data["browse_link"])
        SrrTask.objects(_id=_id).update_one(set__bw_path=data["bw_path"])
        SrrTask.objects(_id=_id).update_one(set__operon_path=data["operon_path"])
        SrrTask.objects(_id=_id).update_one(set__method=data["method"])
        SrrTask.objects(_id=_id).update_one(set__add_time=datetime.now())
        if not os.path.exists(data["bw_path"]):
            os.makedirs(data["bw_path"])
        os.system("mv " + old_bw_path + " " + data["bw_path"])
        if not os.path.exists(data["operon_path"]):
            os.makedirs(data["operon_path"])
        os.system("mv " + old_operon_path + " " + data["operon_path"])
        flash("edit done !", "ok")
        return redirect(url_for("admin.srr_task_edit", _id=_id))
    return render_template("admin/srr_task_edit.html", form=srr_task_form, srr_task=srr_task_query)


@admin.route("/srr_task/del/<_id>/", methods=['GET'])
@admin_login_req
def srr_task_del(_id=None):
    SrrTask.objects(_id=_id).delete()
    flash("delete it done !", "ok")
    return redirect(url_for("admin.srr_task"))


# Task id
@admin.route("/task_id/")
@admin_login_req
def task_id():
    return redirect(url_for("admin.task_id_page", page=1))


@admin.route("/task_id/<int:page>/", methods=['GET'])
@admin_login_req
def task_id_page(page=None):
    page_data = TaskId.objects().paginate(page=page, per_page=10)
    return render_template("admin/task_id.html", page_data=page_data)


@admin.route("/task_id/add/", methods=['GET', 'POST'])
@admin_login_req
def task_id_add():
    task_id_form = TaskIDForm()
    if task_id_form.validate_on_submit():
        data = task_id_form.data
        new_task_id = TaskId(srr_id=data["srr_id"], email=data["email"], task_time=datetime.now())
        new_task_id.save()
        flash("this task is added !", "ok")
        return redirect(url_for("admin.task_id_add"))
    return render_template("admin/task_id_add.html", form=task_id_form)


@admin.route("/task_id/edit/<_id>", methods=['GET', 'POST'])
@admin_login_req
def task_id_edit(_id=None):
    task_id_form = TaskIDForm()
    task_id_query = TaskId.objects.get_or_404(_id=_id)
    if task_id_form.validate_on_submit():
        data = task_id_form.data
        data_count = Specie.objects(srr_id=data["srr_id"]).count()
        if data_count == 0:
            TaskId.objects(_id=_id).update_one(set__srr_id=data["srr_id"])
            TaskId.objects(_id=_id).update_one(set__email=data["email"])
            TaskId.objects(_id=_id).update_one(set__task_time=datetime.now())
            flash("edit done !", "ok")
            return redirect(url_for("admin.task_id_edit", _id=_id))
        elif data_count == 1 and task_id_query.srr_id != data["srr_id"]:
            flash("this task is already exist !", "err")
            return redirect(url_for("admin.task_id_edit", _id=_id))
        elif data_count == 1 and task_id_query.srr_id == data["srr_id"]:
            TaskId.objects(_id=_id).update_one(set__email=data["email"])
            TaskId.objects(_id=_id).update_one(set__task_time=datetime.now())
            flash("edit done !", "ok")
            return redirect(url_for("admin.task_id_edit", _id=_id))
    return render_template("admin/task_id_edit.html", form=task_id_form, task_id=task_id_query)


@admin.route("/task_id/del/<_id>/", methods=['GET'])
@admin_login_req
def task_id_del(_id=None):
    TaskId.objects(_id=_id).delete()
    flash("delete it done !", "ok")
    return redirect(url_for("admin.task_id"))
