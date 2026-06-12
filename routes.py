from ext import app, db
from flask import render_template, redirect, flash
from forms import RegisterForm, JobForm, LoginForm
from models import Job, Review, User, UniquenessRequest
from flask_login import login_user, logout_user, login_required, current_user
from os import path


@app.route("/")
def home():
    jobs = Job.query.all()
    return render_template("index.html", jobs=jobs)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data,
                        password=form.password.data)
        new_user.create()
        flash("წარმატებით დარეგისტრირდი")
        return redirect("/")
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.username == form.username.data).first()
        if user:
            login_user(user)
            flash("წარმატებით შეხვედი საიტზე!")
            return redirect("/")
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


@app.route("/add_job", methods=["GET", "POST"])
@login_required
def add_job():
    form = JobForm()
    if form.validate_on_submit():
        img = form.image.data
        img_filename = "default.jpg"
        if img and img.filename:
            directory = path.join(app.root_path, "static", "images", img.filename)
            img.save(directory)
            img_filename = img.filename

        if current_user.role == "Admin":
            new_job = Job(
                title=form.title.data,
                category=form.category.data,
                salary=form.salary.data,
                danger_level=form.danger_level.data,
                description=form.description.data,
                img=img_filename
            )
            new_job.create()
            flash("Job წარმატებით დაემატა!")
        else:
            new_request = UniquenessRequest(
                user_id=current_user.id,
                title=form.title.data,
                category=form.category.data,
                salary=form.salary.data,
                danger_level=form.danger_level.data,
                description=form.description.data,
                img=img_filename,
                message_to_admin=form.message_to_admin.data
            )
            new_request.create()
            flash("შენი job გაიგზავნა ადმინთან განსახილველად!")

        return redirect("/")
    return render_template("add_job.html", form=form)


@app.route("/update_job/<int:job_id>", methods=["GET", "POST"])
@login_required
def update_job(job_id):
    if current_user.role != "Admin":
        flash("მხოლოდ ადმინს შეუძლია job-ის რედაქტირება!")
        return redirect("/")
    job = Job.query.get(job_id)
    form = JobForm(title=job.title, category=job.category,
                   salary=job.salary, danger_level=job.danger_level,
                   description=job.description)
    if form.validate_on_submit():
        job.title = form.title.data
        job.category = form.category.data
        job.salary = form.salary.data
        job.danger_level = form.danger_level.data
        job.description = form.description.data
        image = form.image.data
        if image and image.filename:
            directory = path.join(app.root_path, "static", "images", image.filename)
            image.save(directory)
            job.img = image.filename
        job.save()
        return redirect("/")
    return render_template("add_job.html", form=form)


@app.route("/delete_job/<int:job_id>")
@login_required
def delete_job(job_id):
    if current_user.role != "Admin":
        flash("მხოლოდ ადმინს შეუძლია job-ის წაშლა!")
        return redirect("/")
    job = Job.query.get(job_id)
    job.delete()
    return redirect("/")


@app.route("/job/<int:job_id>")
def view_job_details(job_id):
    job = Job.query.get(job_id)
    reviews = Review.query.filter(Review.job_id == job_id).all()
    return render_template("job_details.html", job=job, reviews=reviews)


@app.route("/category/<category>")
def show_category(category):
    jobs = Job.query.filter(Job.category.ilike(category)).all()
    if not jobs:
        return render_template("not_found.html", message=f"No jobs found in category: {category}"), 404
    return render_template("category.html", jobs=jobs, category=category)


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/admin/requests")
@login_required
def admin_requests():
    if current_user.role != "Admin":
        flash("ეს გვერდი მხოლოდ ადმინისთვისაა!")
        return redirect("/")
    all_requests = UniquenessRequest.query.order_by(
        UniquenessRequest.id.desc()
    ).all()
    return render_template("admin_requests.html", requests=all_requests)

@app.route("/admin/requests/<int:request_id>/approve")
@login_required
def approve_request(request_id):
    if current_user.role != "Admin":
        return redirect("/")
    req = UniquenessRequest.query.get(request_id)
    if req and req.status == "pending":
        # request-იდან ახალი Job-ი იქმნება
        new_job = Job(
            title=req.title,
            category=req.category,
            salary=req.salary,
            danger_level=req.danger_level,
            img=req.img,
            description=req.description
        )
        new_job.create()
        req.status = "approved"
        req.save()
        flash(f"✅ {req.user.username}-ის job '{req.title}' დამტკიცდა და საიტზე დაემატა!")
    return redirect("/admin/requests")

@app.route("/admin/requests/<int:request_id>/reject")
@login_required
def reject_request(request_id):
    if current_user.role != "Admin":
        return redirect("/")
    req = UniquenessRequest.query.get(request_id)
    if req and req.status == "pending":
        req.status = "rejected"
        req.save()
        flash(f"❌ {req.user.username}-ის job '{req.title}' უარყოფილია!")
    return redirect("/admin/requests")


