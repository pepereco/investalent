from wtforms import Form, HiddenField
from wtforms import validators
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField, IntegerField
from flask_wtf.file import FileField, FileRequired
from wtforms.fields.html5 import EmailField
from flask import flash
from .models import User,Idea

def codi_validator(form, field):
    if field.data=='codi':
        raise validators.ValidationError('Username codi not admited')

class LoginForm(Form):
    username= StringField('Username', [validators.length(min=4, max=50, message='El username se encunetra fuera de rango')])
    password= PasswordField('Password', [validators.Required(), validators.Required(message='El email es requerido')])
class RegisterForm(Form):
    username= StringField('Username',
    [validators.length(min=4,max=50),
    validators.Required(message='The username is required')])
    email = EmailField('Email',
        [validators.length(min=6, max=100),
        validators.Required(message='The email is required'),
        validators.Email(message='Ingress a valid email')])
    password= PasswordField('Password',
        [validators.Required('The password is required'),
        validators.EqualTo('confirm_password', message='The password do not match')])
    confirm_password=PasswordField('Confirm password')
    accept = BooleanField('Accept terms and conditions', [
        validators.DataRequired()])
    honeypot=HiddenField("", [validators.length(max=1)])


    def validate_username(self, username):
        if User.get_by_username(username.data):
            raise validators.ValidationError('Username already in use')

    def validate_email(self, email):
        if User.get_by_email(email.data):
            raise validators.ValidationError('Email already in use')

    def validate(self):
        if not Form.validate(self):
            return False

        if len(self.password.data) < 3:
            self.password.errors.append('Password too short')
            return False

        return True

class TaskForm(Form):
    title= StringField('Title', [
        validators.length(min=4, max= 50, message='Title out of range'),
        validators.DataRequired(message= 'Title required')
        ])
    description= TextAreaField('Description', [
        validators.DataRequired(message='The description is required')
        ], render_kw={'rows':5})
class ProfileForm(Form):
    name= StringField('Name',
        [validators.length(min=1,max=20),
        validators.Required(message='The name is required')])
    last_name = StringField('Last name',
        [validators.length(min=1, max=30),
        validators.Required(message='The last name is required')])
    first_hab= SelectField('First hability', choices= [('1','None'), ('2','Project Manager'),
                                                    ('3','First_hab'), ('4','Second_hab'), ('5','Third_hab')])
    second_hab= SelectField('Second hability', choices= [('1','None'), ('2','Project Manager'),
                                                    ('3','First_hab'), ('4','Second_hab'), ('5','Third_hab')])
    third_hab= SelectField('Third hability', choices=  [('1','None'), ('2','Project Manager'),
                                                    ('3','First_hab'), ('4','Second_hab'), ('5','Third_hab')])
    telephone= StringField('Telephone', [validators.length(min=9, max=15),
                            validators.Required(message='The telephone is required')])
    email = EmailField('Email',
        [validators.length(min=6, max=100),
        validators.Required(message='The email is required'),
        validators.Email(message='Ingress a valid email')])

class IdeaForm(Form):
    problem= TextAreaField('Problem', [
        validators.DataRequired(message='The problem is required')
        ], render_kw={'rows':3})
    solution= TextAreaField('Solution', [
        validators.DataRequired(message='The solution is required')
        ], render_kw={'rows':5})
    extra_info=TextAreaField('Extra information', render_kw={'rows':5})
    creator_involv=SelectField('Desired involvement in the project', [validators.DataRequired(message='The involvement is required')], choices=  [('recommendedProjectManager','Idea creator + Project manager'),('idea','Idea creator'),
                                                    ('recommendedProjectMaker','Idea creator + Project developer')])
class SelectIdeaForm(Form):
    type=SelectField('State of idea:',[validators.Required(message='The type is required')],
                        choices=[('1','New ones'), ('2','Accepted'), ('3', 'Declined')], default='1')

class SelectEvaluation(Form):
    eval=SelectField('Stars:',[validators.Required(message='The evaluation is required')],
                        choices=[('0','0'),('1','1'), ('2','2'), ('3', '3'), ('4', '4'), ('5', '5')], default='3')

class RecomendationTaskForm(Form):
    recomend_user= StringField('Send to user',
                                [validators.length(min=0,max=50)], default='')

    def validate_recomend_user(self,recomend_user):
        if not (User.get_by_username(recomend_user.data) or recomend_user.data==''):
            raise validators.ValidationError('This username is not correct')
        return True

class NewProjectForm(Form):
    title = StringField('Project Name',
        [validators.length(min=1,max=20),
        validators.Required(message='The project name is required')],default='')
    atractive_description = TextAreaField('Short description', [
        validators.DataRequired(message='The short description is required')
        ], render_kw={'rows':2})
    description = TextAreaField('Description (Problem/Solution)', [
        validators.DataRequired(message='The description is required')
        ], render_kw={'rows':5})
    num_fases=SelectField('Duration of the project:',[validators.Required(message='The duration is required')],
                        choices=[('1','3 months'), ('2','6 months'), ('3', '9 months')], default='1')
    gen_obj_F1= TextAreaField('Objectives fase 1', [validators.Required(message='The objective is required')],
                                    render_kw={'rows':5}, default='stopValue')
    percent_F1= IntegerField('Percent of fase 1', [validators.Required(message='The % is required')], default='NonValue')
    gen_obj_F2= TextAreaField('Objectives fase 2', [validators.Required(message='The objective is required')], render_kw={'rows':5}, default="Objectives fase 2")
    percent_F2= IntegerField('Percent of fase 2', [validators.Required(message='The % is required')], default='NonValue')
    gen_obj_F3= TextAreaField('Objectives fase 3', [validators.Required(message='The objective is required')], render_kw={'rows':5}, default="Objectives fase 3")
    percent_F3= IntegerField('Percent of fase 3', [validators.Required(message='The % is required')], default='NonValue')
    recomend_project_manager = StringField('Send to project manager',
                                [validators.length(min=0,max=50)], default='')
    ceo_key= StringField('Secure with a key',[validators.length(min=0,max=20)], default=None)
    hide = SelectField('Privacity:',[validators.Required(message='The privacity is required')],
                        choices=[('0','Public'), ('1','Private')], default='0')

    def validate_recomend_project_manager(self,recomend_project_manager):
        if not (User.get_by_username(recomend_project_manager.data) or recomend_project_manager.data==''):
            raise validators.ValidationError('This username is not correct')
        return True

    def validate_percent_F1(self, percent_F1):
        if percent_F1.data!='NonValue':
            if int(percent_F1.data)>100 or int(percent_F1.data)<=0 :
                self.percent_F2.data='0'

                raise validators.ValidationError('This must be a correct %')

    def validate_percent_F2(self, percent_F2):
        if percent_F2.data!='NonValue':
            if int(percent_F2.data)>100 or int(percent_F2.data)<=0:
                self.percent_F2.data='0'

                raise validators.ValidationError('This must be a correct %')


    def validate_percent_F3(self, percent_F3):
        if percent_F3.data!='NonValue':
            if int(percent_F3.data)>100 or int(percent_F3.data)<=0:
                self.percent_F2.data='0'

                raise validators.ValidationError('This must be a correct %')

    def validate_sum_percent(self):
        if self.percent_F1.data=='NonValue':
            return True

        if self.percent_F2.data=='NonValue':
            self.percent_F2.data='0'
        if self.percent_F3.data=='NonValue':
            self.percent_F3.data='0'

        if (int(self.percent_F1.data)+int(self.percent_F2.data)+int(self.percent_F3.data)!=100):
            flash ('the sum of % must be 100')
            return False
        else:
            return True

class SelectProjectPhase(Form):
    state=SelectField('Phase of the project:',[validators.Required(message='The phase is required')],
                        choices=[('1','New ones'), ('2','Phase 1'), ('3', 'Phase 2'), ('4', 'Phase 3')], default='1')

class SelectProjectPhaseAdmin(Form):
    state=SelectField('Phase of the project:',[validators.Required(message='The phase is required')],
                        choices=[('1','New ones'), ('2','Phase 1'), ('3', 'Phase 2'), ('4', 'Phase 3'), ('5', 'All')], default='5')
    project_searcher = StringField('Search by title: ', [validators.length(min=1,max=20)],default='')


class SelectProjectTypeHab(Form):
    typeHab=SelectField('Projects as:',[validators.Required(message='The hability is required')],
                        choices=[('1','Project Manager'), ('2','Idea creator'), ('3', 'CEO')], default='1')

class SelectFindTask(Form):
    SelectTask=SelectField('Find:',[validators.Required(message='The hability is required')],
                        choices=[('1','Recommended'), ('2','All'), ('3', 'First_hab'), ('4', 'Second_hab'), ('5', 'Third_hab')], default='1')

class Select_all_task(Form):
    SelectTask=SelectField('Find:',[validators.Required(message='The hability is required')],
                        choices=[('2','All'), ('3', 'First_hab'), ('4', 'Second_hab'), ('5', 'Third_hab')], default='2')
    task_searcher = StringField('Milestone title', [validators.length(min=1,max=20)],default='')

class SelectTaskPhase(Form):
    SelectTaskPhase=SelectField('Find:',[validators.Required(message='The phase is required')],
                        choices=[('1','On course'), ('2','Finished')], default='1')

class Edit_description_project(Form):
    description = TextAreaField('Description (Problem/Solution)', [
        validators.DataRequired(message='The description is required')
        ], render_kw={'rows':5})

class Intro_project_key(Form):
    key = StringField('Secure with a key',[validators.length(min=0,max=20)])

class Edit_atractive_description_project(Form):
    atractive_description = TextAreaField('Short description', [
        validators.DataRequired(message='The short description is required')
        ], render_kw={'rows':2})

class Edit_title_project(Form):
    title = StringField('Project Name',
        [validators.length(min=1,max=20),
        validators.Required(message='The project name is required')])

class Edit_obj_per_1(Form):
    gen_obj_F1=TextAreaField('Objectives fase 1', [validators.Required(message='The objective is required')], render_kw={'rows':5})
    work_percent_F1=IntegerField('Percent of fase 1', [validators.Required(message='The % is required')], default=0)


    def validate_edited_percent_1(self):
        if (int(self.work_percent_F1.data)!=100):
            flash ('the sum must be 100')
            return False
        else:
            return True


class Edit_obj_per_2(Form):
    gen_obj_F1=TextAreaField('Objectives fase 1', [validators.Required(message='The objective is required')], render_kw={'rows':5})
    work_percent_F1=IntegerField('Percent of fase 1', [validators.Required(message='The % is required')], default=0)
    gen_obj_F2=TextAreaField('Objectives fase 2', [validators.Required(message='The objective is required')], render_kw={'rows':5})
    work_percent_F2=IntegerField('Percent of fase 2', [validators.Required(message='The % is required')], default=0)
    def validate_edited_percent_2(self):
        if (int(self.work_percent_F1.data)+int(self.work_percent_F2.data)!=100):
            flash ('the sum must be 100')
            return False
        else:
            return True

class Edit_obj_per_3(Form):
    gen_obj_F1=TextAreaField('Objectives fase 1', [validators.Required(message='The objective is required')], render_kw={'rows':5})
    work_percent_F1=IntegerField('Percent of fase 1', [validators.Required(message='The % is required')], default=0)
    gen_obj_F2=TextAreaField('Objectives fase 2', [validators.Required(message='The objective is required')], render_kw={'rows':5})
    work_percent_F2=IntegerField('Percent of fase 2', [validators.Required(message='The % is required')], default=0)
    gen_obj_F3=TextAreaField('Objectives fase 3', [validators.Required(message='The objective is required')], render_kw={'rows':5})
    work_percent_F3=IntegerField('Percent of fase 3', [validators.Required(message='The % is required')], default=0)

    def validate_edited_percent_3(self):
        if (int(self.work_percent_F1.data)+int(self.work_percent_F2.data)+int(self.work_percent_F3.data)!=100):
            flash ('the sum must be 100')
            return False
        else:
            return True

'''

class Upload_presentation(Form):
    presentation= FileField(validators=[FileRequired()])

'''
class Create_task(Form):
    title = StringField('Milestone title',
        [validators.length(min=1,max=20),
        validators.Required(message='The milestone is required')])
    description = TextAreaField('Description', [
        validators.DataRequired(message='The description is required')
        ], render_kw={'rows':5})
    hability_1=SelectField('First hability',[validators.Required(message='The first hability is required')], choices= [('1','None'),('3','UserType1'),
                                                    ('4','UserType2'), ('5','UserType3')], default='1')
    hability_2= SelectField('Second hability', [validators.Required(message='The first hability is required')],choices= [('1','None'),('3','UserType1'),
                                                    ('4','UserType2'), ('5','UserType3')], default='1')
    months=SelectField('Months', [validators.Required(message='The months are required')],choices= [('1','None'), ('2','1'),
                                                    ('3','2'), ('4','3')], default='1')
    days= IntegerField('Days', [ validators.NumberRange(min=0 , max=31, message='The days must be between 0 and 31')], default=0)
    work= IntegerField('% of Phase', [validators.Required(message='The work is required'), validators.NumberRange(min=0, max=100, message='The % must be between 0 and 100')])
    recomend_user= StringField('Send to user',
                                [validators.length(min=0,max=50)], default='')
    commitment= SelectField('Commitment to the project',[validators.Required(message='The commitment is required')], choices= [('1','Not commited'),
                                                    ('2','Commited')], default='1')
    objectives= TextAreaField('Objectives', [
                validators.DataRequired(message='The objectives are required')
                ], render_kw={'rows':5})

    def validate_recomend_user(self,recomend_user):
        if not (User.get_by_username(recomend_user.data) or recomend_user.data==''):
            raise validators.ValidationError('This username is not correct')
        return True
