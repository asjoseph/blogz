from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, user):
        self.title = title
        self.body = body
        self.user = user


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blog = db.relationship('Blog', backref='owner')

    def __init__(self, user, email, password):
        self.user = user
        self.email = email
        self.password = password

@app.route('/blog', methods=['GET'])
def home():
    if 'email' not in session:
       return redirect('/login')

    if request.args:
        allByUser = request.args.get("allByUser")
        blog_id = request.args.get("id")
        user = request.args.get("user")
        if blog_id != None:
            blogs = Blog.query.filter_by(id=blog_id)
        if user != None:
            blogs = Blog.query.filter_by(user_id=user)
        if allByUser != None:
            email = session.get("email")
            user = User.query.filter_by(email=email).first()
            blogs = Blog.query.filter_by(user_id=user.id)
        return render_template('home.html', blogs=blogs)
    else:
        return render_template('home.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['Username']
        password = request.form['Password']
        verify = request.form['Verify Password']
        email = request.form['Email']
        new_user = User(username, email, password)
        db.session.add(new_user)
        db.session.commit()
        session['email'] = email
        return redirect("/")
    else:
        return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged in")
            print(session)
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')


@app.route('/', methods=['GET'])
def index():

    blogs = Blog.query.all()
    if request.args:
        user_id = request.args.get("id")

    return render_template('home.html', blogs=blogs)

@app.route('/newpost', methods=['GET', 'POST'])
def add_blog():
    if 'email' not in session:
        return redirect('/login')

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        user = User.query.filter_by(email=session['email']).first()

        if len(blog_title) < 1:
            title_error = "Please fill in the title"

        if len(blog_body) < 1:
            body_error = "Please fill in the body"

        if blog_title and blog_body:
            blog = Blog(blog_title, blog_body, user.id)
            db.session.add(blog)
            db.session.commit()
            return render_template('singleBlogEntry.html',blog=blog,user=user)
        else:
            return render_template('newBlogForm.html', title_error=title_error,
                                   body_error=body_error)
    else:

        return render_template('newBlogForm.html')


@app.route('/logout')
def logout():
    del session['email']
    return redirect('/login')

if __name__ == '__main__':
    app.run()
