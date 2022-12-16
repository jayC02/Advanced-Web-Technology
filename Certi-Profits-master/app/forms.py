from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DateField, DateTimeField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User
from flask_wtf.file import FileField, FileRequired, FileAllowed

class CommentForm(FlaskForm):
  # Define the body field as a required TextAreaField
  body = TextAreaField('Leave a comment?', validators=[DataRequired()])
  # Define the submit field as a SubmitField
  submit = SubmitField('Submit')

# Define the EditProfileForm class
class EditProfileForm(FlaskForm):
  username = StringField('Username', validators=[DataRequired()])
  email = StringField('Email', validators=[DataRequired(), Email()])
  about_me = TextAreaField('About me', validators=[Length(min=0, max=200)])
  profilepic = FileField(validators=[FileAllowed(['png'], 'Png only')])
  submit = SubmitField('Submit')

  # Initialize the original_username and original_email attributes
  def __init__(self, original_username, original_email, *args, **kwargs):
    super(EditProfileForm, self).__init__(*args, **kwargs)
    self.original_username = original_username
    self.original_email = original_email

  def validate_username(self, username):
    # If the entered username is different from the original username
    if username.data != self.original_username:
      # Check if the entered username is already in use by another user
      user = User.query.filter_by(username=self.username.data).first()
      if user:
        raise ValidationError('Username already taken')

  def validate_email(self, email):
    if email.data != self.original_email:
      user = User.query.filter_by(email=self.email.data).first()
      if user:
        raise ValidationError('This email has already been used, try another email.')
    
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    profilepic = FileField(validators=[
                            FileRequired(),
                            FileAllowed(['png'], 'Only png!') ])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class PostForm(FlaskForm):
    title = StringField('Ticker Name', validators=[DataRequired()])
    venue = StringField('Bullish or Bearish', validators=[DataRequired()])
    post = TextAreaField('Due Dilligence', validators=[DataRequired()])
    time = DateTimeField('Buy/sell time HH:MM', format='%H:%M', validators=[DataRequired()])
    submit = SubmitField('Submit')

class EditPostForm(FlaskForm):
    title = StringField('Ticker Name', validators=[DataRequired()])
    venue = StringField('Bullish or Bearish', validators=[DataRequired()])
    post = TextAreaField('Due Dilligence', validators=[DataRequired()])
    time = DateTimeField('Buy/sell time HH:MM', format='%H:%M', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, original_title, original_date, original_time,
                 original_venue, original_post, *args, **kwargs):
        super(EditPostForm, self).__init__(*args, **kwargs)
        self.original_title = original_title
        self.original_date = original_date
        self.original_time = original_time
        self.original_venue = original_venue
        self.original_post = original_post

class ResetP(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class PrivateMessages(FlaskForm):
    message = TextAreaField('Message', validators=[
        DataRequired(), Length(min=0, max=140)])
    submit = SubmitField('Submit')
