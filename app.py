from flask import Flask, render_template, request, redirect, flash,url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from forms import RegistrationFrom, LoginFrom

from sqlalchemy import Enum

app = Flask('__name__')
app.config ["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///test.db'
db = SQLAlchemy(app)
app.config ['SECRET_KEY'] = 'ZOMn8n1Jt8KTfXPwbcZ3tw'


class Task(db.Model):
    """Task class
    Attributes:
        id (int): Unique id, primary key, auto increment.
        username (str): Foreign key referencing Users table.
        task (str): Details of the task.
        status (enum): Status of the task, with the following values
            - 'to_do'
            - 'doing'
            - 'done'
    """

    id = db.Column(db.Integer, primary_key=True)
    # username = db.relationship('User')
    content = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(Enum('to_do', 'doing', 'done'))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String)

    def __repr__(self):
        return f"User ('{self.login}')"


@app.route('/')
def home():
    return render_template('base.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginFrom()
    if form.validate_on_submit():
        if form.email.data == 'markre94@icloud.com' and form.password.data == "elo":
            flash(f'You are now logged in as {form.email.data}!', 'success')
            return redirect(url_for('index'))
        else:
            flash("Login unsuccessful", "danger")
    return render_template(template_name_or_list='login.html', form=form, title="Login")


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegistrationFrom()
    if form.validate_on_submit():
        flash(f"User created for {form.username.data}!", 'success')
        return redirect(url_for('index'))
    return render_template(template_name_or_list='sign_in.html', form=form, title="Register")


@app.route('/app', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        try:
            task_content = request.form ['content']
            if task_content == '':
                flash('The task must contain something.', 'warning')
                return redirect('/app')
            else:
                new_task = Task(content=task_content, status='to_do')

                try:
                    db.session.add(new_task)
                    db.session.commit()
                    return redirect('/app')
                except:
                    return 'There was an issue adding your task'
        except:
            flash("Ups forgot to add file")
    else:
        tasks = Task.query.order_by(Task.date_created).all()

        return render_template('main.html', tasks=tasks)


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Task.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/app')
    except:
        return "There was an problem "


@app.route('/task/<status>/<int:id>')
def take_task(status, id):
    task_to_take = Task.query.get_or_404(id, status)
    try:
        if task_to_take.status == "to_do":

            task_to_take.status = "doing"
            db.session.commit()
            return redirect('/app')
        elif task_to_take.status == "doing":
            task_to_take.status = "done"
            db.session.commit()
            return redirect('/app')
        else:
            task_to_take.status = "done"
            db.session.commit()
            return redirect('/app')
    except:
        return "There was an problem "


@app.route('/discard/<int:id>')
def discard(id):
    task_to_take = Task.query.get_or_404(id)
    try:
        task_to_take.status = "to_do"
        db.session.commit()
        return redirect('/app')
    except:
        return "There was an problem "


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
