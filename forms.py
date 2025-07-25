from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class CreateListForm(FlaskForm):
    name = StringField('List Name', validators=[DataRequired(), Length(min=1, max=100)])
    submit = SubmitField('Create List')

class CreateItemForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=200)])
    submit = SubmitField('Add Item')

class EditItemForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=200)])
    status = SelectField('Status', choices=[
        ('TODO', 'TODO'),
        ('IN_PROGRESS', 'IN PROGRESS'),
        ('DONE', 'DONE')
    ], validators=[DataRequired()])
    submit = SubmitField('Update Item')
