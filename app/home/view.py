# coding:utf8
from . import home
from flask import render_template, redirect, url_for


@home.route("/")
def index():
    return render_template("home/index.html")


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
