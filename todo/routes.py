from flask import render_template, url_for, flash, redirect, request, abort
from todo import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from todo.models import User, Todo
from todo.forms import LoginForm, RegistrationForm, TodoForm

@app.route("/")
@app.route("/index", methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    login_form = LoginForm()
    register_form = RegistrationForm()

    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user, remember=login_form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    if register_form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(register_form.password.data).decode('utf-8')
        user = User(username=register_form.username.data, email=register_form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('index'))

    return render_template('index.html', title='Please login or register!', register_form=register_form, login_form=login_form)

@app.route("/home", methods=['GET', 'POST'])
@login_required
def home():
    todo_form = TodoForm()
    if todo_form.validate_on_submit():
        task = Todo(title=todo_form.task.data, priority=todo_form.priority.data, status='In Progress', user_id=current_user.id)
        db.session.add(task)
        db.session.commit()
        flash('Your task has been added!', 'success')
        return redirect(url_for('home'))
    if request.method == 'GET':
        tasks = Todo.query.order_by(Todo.date_posted).filter_by(user_id=current_user.id, status="In Progress")
        return render_template('home.html', title='Your things todo!', todo_form=todo_form, tasks=tasks)

@app.route("/finishtask/<int:task_id>", methods=['POST'])
@login_required
def finish_task(task_id):
    task = Todo.query.get_or_404(task_id)
    task.status = "Completed"
    db.session.commit()
    flash('Task completed!', 'success')
    return redirect(url_for('home'))

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))