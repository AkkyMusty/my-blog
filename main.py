import datetime

from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date

'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
ckeditor = CKEditor(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy()
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


class PostForm(FlaskForm):
    title = StringField('blog title', validators=[DataRequired()])
    subtitle = StringField('subtitle', validators=[DataRequired()])
    author = StringField('author', validators=[DataRequired()])
    image = StringField('image', validators=[DataRequired(), URL()])
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField('Submit post')

with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():
    # TODO: Query the database for all the posts. Convert the data to a python list.
    posts = []
    all_blog = db.session.execute(db.select(BlogPost)).scalars().all()
    if all_blog:
        for blog in all_blog:
            posts.append(blog)
    return render_template("index.html", all_posts=posts)


# TODO: Add a route so that you can click on individual posts.
@app.route('/post/<post_id>')
def show_post(post_id):
    # TODO: Retrieve a BlogPost from the database based on the post_id
    requested_post = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()
    return render_template("post.html", post=requested_post)


# TODO: add_new_post() to create a new blog post

@app.route("/new-post", methods=["GET", "POST"])
def new_post():
    post_heading = "New Post"
    post_form = PostForm()
    if post_form.validate_on_submit():
        time = datetime.datetime.now()
        new_post = BlogPost()
        new_post.title=post_form.title.data
        new_post.subtitle=post_form.subtitle.data
        new_post.date=time.strftime("%B %d, %y")
        new_post.body = post_form.body.data
        new_post.author = post_form.author.data
        new_post.img_url = post_form.image.data
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))

    return render_template("make-post.html", form=post_form, heading=post_heading)


# TODO: edit_post() to change an existing blog post
@app.route("/edit-post/<post_id>", methods=["GET","POST", "PATCH"])
def edit_post(post_id):
    post_heading = "Edit Post"
    requested_post = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()
    edit_form = PostForm(title = requested_post.title,
                         subtitle = requested_post.subtitle,
                         author = requested_post.author,
                         image = requested_post.img_url,
                         body = requested_post.body)
    if edit_form.validate_on_submit():
        edit_post = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()
        edit_post.title = edit_form.title.data
        edit_post.subtitle = edit_form.subtitle.data
        edit_post.date = edit_post.date
        edit_post.body = edit_form.body.data
        edit_post.author = edit_form.author.data
        edit_post.img_url = edit_form.image.data
        db.session.commit()
        return redirect(url_for('show_post', post_id=post_id))


    return render_template("make-post.html", form=edit_form, heading=post_heading)

# TODO: delete_post() to remove a blog post from the database
@app.route("/delete/<post_id>")
def delete_post(post_id):
    post_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
