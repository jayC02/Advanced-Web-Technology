from flask import Flask, render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, ResetP, ResetPasswordForm, PrivateMessages, CommentForm, EditPostForm
from app.models import User, Post, Message, Notification, UserList, Comment
from werkzeug.urls import url_parse
from datetime import datetime
from app.email import send_password_reset_email
import os
from PIL import Image

@app.route('/like/<user_id>/<post_id>')
@login_required
def like(post_id, user_id):
    # Check if the user is already like in this event
    if UserList.query.filter_by(post_id=post_id).filter_by(user_id=user_id)[0] is None:
        post = Post.query.get(post_id)
        # If not, add the user to the list of like users
        item = UserList(
        post_id=post_id,
        user_id=user_id,
        event_interested=post)
        db.session.add(item)
        db.session.commit()
        flash('You liked this post')
        return redirect(url_for('explore'))
    else:
        flash('You have already liked this post')
        return redirect(url_for('explore'))

@app.route('/dislike/<user_id>/<post_id>')
@login_required
def dislike(post_id, user_id):
    relation = UserList.query.filter_by(post_id=post_id).filter_by(user_id=user_id)[0]
    db.session.delete(relation)
    db.session.commit()
    flash('You dislike this post')
    return redirect(url_for('explore'))

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    # Create a form for editing the user's profile
    form = EditProfileForm(current_user.username, current_user.email)

    if form.validate_on_submit():
        try:
            # If the user selected a profile picture, save it
            file = request.files['profilepicture']
            filename = form.username.data + '.png'
            file.save(os.path.join(app.root_path, 'static/profile_pics', filename))
            current_user.profilepic = url_for('static', filename='profile_pics/' + filename)
        except:
            pass

        # Update the user's profile with the new data from the form
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        current_user.email = form.email.data
        db.session.commit()

        flash('Changes saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        # If the user is accessing the page for the first time,
        # populate the form with the user's current data
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
        form.email.data = current_user.email

    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

# Define the index route and protect it with the login_required decorator
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
  # Create a PostForm object
  form = PostForm()

  # If the form has been submitted and is valid, create a Post object using the form data
  if form.validate_on_submit():
    eventphoto = request.files['eventphoto']
    photoname = form.title.data + '.png'
    eventphoto.save(os.path.join(app.root_path, 'static/event_pics/', photoname))
    post = Post(
        title=form.title.data,
        eventphoto=url_for('static', filename='event_pics/' + photoname),
        date=form.date.data,
        time=form.time.data,
        venue=form.venue.data,
        body=form.post.data,
        author=current_user,
    )
    db.session.add(post)
    db.session.commit()
    flash('Your event has been posted :)')
    return redirect(url_for('explore'))

  # If the form is not valid, render the index.html template and pass the form object to it
  return render_template('index.html', title='Post Ticker', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('explore'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        return redirect(url_for('explore'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('explore'))
    form = RegistrationForm()
    if form.validate_on_submit():
        file = request.files['profilepic']
        filename = form.username.data + '.png'
        file.save(os.path.join(app.root_path, 'static/profile_pics', filename))
        user = User(username=form.username.data, email=form.email.data, profilepic=url_for('static', filename='profile_pics/' + filename))
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('You are now officially registered')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    image_file = user.profilepic
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(
            Post.timestamp.desc()
            ).paginate(
                    page=page,
                   per_page=app.config['POSTS_PER_PAGE'],
                   error_out=False)
    postList = []
    relations = UserList.query.filter_by(user_id=user.id)
    if relations is not None:
        for relation in relations:
            if relation.post_id is not None:
                new_post = Post.query.get(relation.post_id)
                postList.append(new_post)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items, postList=postList,
                           next_url=next_url, prev_url=prev_url, image_file=image_file)

@app.route("/user/delete/<username>", methods=['GET', 'POST'])
@login_required
def delete_user(username):
    user = User.query.filter_by(username=username).first()
    if user.username != current_user.username:
        abort(403)
    db.session.delete(user)
    db.session.commit()
    flash('User has been Deleted')
    return redirect(url_for('login'))

@app.route("/post/<post_id>")
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    comments = post.comments.order_by(Comment.timestamp.desc())
    return render_template('showEvent.html', post=post, comments=comments)

@app.route('/post/<post_id>/comment', methods=['GET', 'POST'])
@login_required
def comment(post_id):
    # Get the post from the database
    post = Post.query.get(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        # Create a new comment
        comment = Comment(
            username = current_user.username,
            body = form.body.data,
            post = post)
        db.session.add(comment)
        db.session.commit()
        flash('Comment posted')
    # Get all the comments for the post, ordered by timestamp in descending order
    comments = post.comments.order_by(Comment.timestamp.desc())
    return render_template('showEvent.html', form=form, post=post, comments=comments)
    
@app.route('/post/<post_id>/delete_comment/<comment_id>', methods=['GET', 'POST'])
@login_required
def delete_comment(post_id, comment_id):
    post = Post.query.get_or_404(post_id)
    comment = Comment.query.get_or_404(comment_id)
    if (comment.username != current_user.username) or (post.author != current_user):
        flash("You can't delete the message if it's not yours or you don't own the event!")
        abort(403)
    else:
        db.session.delete(comment)
        db.session.commit()
        flash('You comment has been deleted.')
        return redirect(url_for('post', post_id=post_id))

@app.route("/post/<post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    # Get the post from the database, or return a 404 error if it doesn't exist
    post = Post.query.get_or_404(post_id)
    # Check if the current user is the author of the post
    if post.author != current_user:
        flash('Unable to edit post')
        print('Cannot edit post')
        # Return a 403 error if the user is not the author
        abort(403)
    form = EditPostForm(post.title, post.date, post.time, post.venue, post.body)
    if form.validate_on_submit():
        # Update the post with the new form data
        post.title = form.title.data
        post.date = form.date.data
        post.time = form.time.data
        pot.venue = form.venue.data
        post.body = form.post.data
        file = request.files['eventphoto']
        filename = form.title.data + '.png'
        # Save the file to the event_pics directory
        file.save(os.path.join(app.root_path, 'static/event_pics', filename))
        # Update the eventphoto field with the URL of the saved file
        post.eventphoto = url_for('static', filename='event_pics/' + filename)
        db.session.commit()
        # Show a success message to the user
        flash('Your post has been updated!')
        # Redirect the user to the post page
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        # Prepopulate the form with the current post data
        form.title.data = post.title
        form.date.data = post.date
        form.time.data = post.time
        form.venue.data = post.venue
        form.post.data = post.body
    # Render the update post template with the form and post data
    return render_template('update_post.html', form=form, post=post)

@app.route("/post/<post_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        flash("Cannot delete a post you didn't create.")
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted.')
    return redirect(url_for('index'))

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('Unable to follow yourself')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/')
@app.route('/discoverevents')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date.asc()).paginate(
            page=page,
            per_page=app.config['POSTS_PER_PAGE']
            )
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("index.html", title='Discover new events!',
            posts=posts.items, next_url=next_url, prev_url=prev_url)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('explore'))
    form = ResetP()
    if form.validate_on_submit():
        # Get the user with the matching email address
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('resetP.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('explore'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = PrivateMessages()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user, body=form.message.data)
        db.session.add(msg)
        user.add_notification('unread_message_count', user.new_messages())
        db.session.commit()
        flash('Your message has been sent.')
        return redirect(url_for('user', username=recipient))
    return render_template('send_message.html', title='Send Message',
                           form=form, recipient=recipient)

@app.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    messages = current_user.messages_received.order_by(
            Message.timestamp.desc()
            ).paginate(
                    per_page=app.config['POSTS_PER_PAGE'],
                    error_out=False
                    )
    next_url = url_for('messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('messages', page=messages.prev_num) \
        if messages.has_prev else None
    return render_template('messages.html', messages=messages.items,
                           next_url=next_url, prev_url=prev_url)
    
@app.route("/messages/delete/<message>", methods=['GET', 'POST'])
@login_required
def delete_message(message):
    message = Message.query.filter_by(id=message).first()
    if not (current_user.is_authenticated):
        abort(403)
    db.session.delete(message)
    db.session.commit()
    flash('Your message has been deleted')
    return redirect(url_for('messages'))

@app.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Message': Message,
            'Notification': Notification}

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


    
        


    
    