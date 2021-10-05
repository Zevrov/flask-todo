from flask import Flask, render_template, request, redirect, url_for
from models import db, Todo, LoginForm, User, RegisterForm
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '\x14B~^\x07\xe1\x197\xda\x18\xa6[[\x05\x03QVg\xce%\xb2<\x80\xa4\x00'
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bootstrap = Bootstrap(app)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    # home page
    return render_template('index.html')

@app.route('/todo')
def todo():
    #show all todos
    todo_list = Todo.query.filter_by(username=current_user.username).all()
    todo_list.sort(key=lambda x: x.priority)
    #for todo in todo_list:
    for this_todo in todo_list:
        this_todo.due_date = this_todo.due_date.strftime("%Y-%m-%d")
    return render_template('todo.html', todo_list=todo_list, name=current_user.username)

@app.route("/add", methods=["POST"])
def add():
    # add new item
    title = request.form.get("title")
    html_date = request.form.get("date")
    py_date = datetime.strptime(html_date, "%Y-%m-%d")
    new_todo = Todo(title=title, complete=False, username=current_user.username, priority=3, due_date=py_date)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("todo"))

@app.route("/update/<int:todo_id>")
def update(todo_id):
    # update an existing item
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("todo"))

@app.route("/promote/<int:todo_id>")
def promote(todo_id):
    # promote an existing item
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.priority = todo.priority + 1
    db.session.commit()
    return redirect(url_for("todo"))

@app.route("/demote/<int:todo_id>")
def demote(todo_id):
    # demote an existing item
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.priority = todo.priority - 1
    db.session.commit()
    return redirect(url_for("todo"))

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    # delete an existing item
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("todo"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # login function
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('todo'))

        return '<h1>Invalid username or password</h1>'

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # create user function
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('signup.html', form=form)

@app.route('/logout')
@login_required
# logout function
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)