from flask_wtf import FlaskForm
from wtforms.fields import (StringField, PasswordField, SelectField,
                            SubmitField, TextAreaField)
from wtforms.validators import DataRequired, equal_to, length
from flask_wtf.file import FileField


class RegisterForm(FlaskForm):
    username = StringField("Enter Username", validators=[
        DataRequired()
    ])
    password = PasswordField("Enter Password", validators=[
        DataRequired(),
        length(min=6, max=24),
    ])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(),
        equal_to("password", message="პაროლები არ ემთხვევა")
    ])

    register = SubmitField("Register")


class LoginForm(FlaskForm):
    username = StringField()
    password = PasswordField()

    login = SubmitField("Log In")


class JobForm(FlaskForm):
    image = FileField("Upload job image")
    title = StringField("Enter Job Title")
    category = StringField("Enter Category")
    salary = StringField("Enter Salary Range")
    danger_level = SelectField("Danger Level", choices=["Low", "Medium", "High"])
    description = StringField("Enter Description")
    message_to_admin = TextAreaField("Message to Admin")

    submit = SubmitField("Add Job")

