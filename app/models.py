import datetime

from flask import send_file
from flask_login import UserMixin
import io
import os
from io import BytesIO
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from . import db

class User(db.Model, UserMixin):
    __tablename__='users'

    id = db.Column(db.Integer, primary_key=True)
    username =db.Column(db.String(50),unique=True, nullable=False)
    encrypted_password = db.Column(db.String(94), nullable=False)
    user_type =db.Column (db.Integer) # 0--> only devel user , 1--> devel + project manager, 2-->only project manager, 3--> admin, 4--> potencial dev + pm , 5--> potencial proj manager
    email = db.Column(db.String(100),unique=True,nullable=False)
    created_at=db.Column(db.DateTime,default=datetime.datetime.now())
    tasks= db.relationship('Task', lazy='dynamic')
    profile= db.relationship('Profile', uselist=False, back_populates='user')
    ideas= db.relationship('Idea', lazy='dynamic')
    com_secret_projects= db.relationship('Comercial_secret',lazy='dynamic')
    note=db.Column(db.Integer) #las notas sobre 10
    num_changes_note=db.Column(db.Integer)
    contracts= db.relationship('Contract',lazy='dynamic')

    def verify_password(self, password):
        return check_password_hash(self.encrypted_password,password)

    @property
    def password(self):
        pass

    @password.setter
    def password(self,value):
        self.encrypted_password= generate_password_hash(value)

    def __str__(self):
        return self.username

    @classmethod
    def create_element(cls, username, password, email ):
        user= User(username=username, password=password, email=email, note=5, num_changes_note=0, user_type=0)

        db.session.add(user)
        db.session.commit()

        return user

    @classmethod
    def change_note_by_id(cls,id, new_note):
        new_note=int(new_note)
        user= User.get_by_id(id)
        note=user.note
        num_changes_note= user.num_changes_note
        sum_notes= note*num_changes_note
        new_sum=sum_notes+new_note
        num_changes_note=num_changes_note+1
        note=new_sum/num_changes_note
        user.note=note
        user.num_changes_note=num_changes_note

        db.session.add(user)
        db.session.commit()

    @classmethod
    def change_user_type(cls,id, user_type):
        user= User.get_by_id(id)
        user.user_type=user_type

        db.session.add(user)
        db.session.commit()

    @classmethod
    def change_email(cls,id, email):
        user= User.get_by_id(id)
        user.email=email

        db.session.add(user)
        db.session.commit()

    @classmethod
    def update_contracts(cls,user_id, task, contract):
        user= User.get_by_id(user_id)
        user.tasks=task

        db.session.add(user)
        db.session.commit()


    @classmethod
    def get_by_username(cls, username):
        return User.query.filter_by(username=username).first()

    @classmethod
    def get_by_id(cls, id):
        return User.query.filter_by(id=id).first()

    @classmethod
    def get_by_email(cls, email):
        return User.query.filter_by(email=email).first()

class Task(db.Model):
    __tablename__='tasks'

    id=db.Column(db.Integer, primary_key=True)
    title= db.Column(db.String(50))
    description= db.Column(db.Text())
    duration= db.Column(db.Integer)
    user_id= db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    start_at = db.Column(db.DateTime)
    teoric_finish = db.Column(db.DateTime)
    state=db.Column(db.Integer) #la tasca esta cogida = 1 , no cogida =0, tasca acabada= 2
    precedent_task_id= db.Column(db.Integer)
    fase= db.Column(db.Integer)
    work= db.Column(db.Integer)
    project_id=db.Column(db.Integer, db.ForeignKey('projects.id'))
    hability_1= db.Column(db.String(50))
    hability_2= db.Column(db.String(50))
    percent=db.Column(db.Float)
    recomend_username= db.Column(db.String(50))
    commitment= db.Column(db.String(20))
    objectives=db.Column(db.Text())
    hide = db.Column(db.Integer)
    applicants=db.relationship('Contract',lazy='dynamic')


    @classmethod
    def create_element(cls, title, description, duration, state, fase, work, project_id, hability_1, hability_2, recomend_username, commitment, objectives, hide):
        task= Task(title=title, description=description, duration=duration, state=state, fase=fase, work=work, project_id=project_id,
                    hability_1=hability_1, hability_2=hability_2, recomend_username=recomend_username, commitment=commitment, objectives=objectives, hide = hide )

        db.session.add(task)
        db.session.commit()

        return task


    @classmethod
    def leave_task(cls, id):
        task=Task.get_by_id(id)
        task.user_id=None
        task.start_at=None
        task.teoric_finish=None
        task.state=0
        task.percent=None

        db.session.add(task)
        db.session.commit()

        return task


    @property
    def little_description(self):
        if len(self.description)>20:
            return self.description[0:19]+'...'
        return self.description


    @classmethod
    def get_by_id(cls,id):
        return Task.query.filter_by(id=id).first()

    @classmethod
    def clear_recommended_username(cls, id):
        task=Task.get_by_id(id)
        task.recomend_username=''
        db.session.add(task)
        db.session.commit()

        return task

    @classmethod
    def update_hide(cls, task_id, hide):
        task=Task.get_by_id(task_id)
        task.hide=hide
        db.session.add(task)
        db.session.commit()


    @classmethod
    def update_element(cls, id, title, description, duration, work, hability_1, hability_2, recomend_username):
        task=Task.get_by_id(id)

        if task is None:
            return False

        task.title=title
        task.description=description
        task.duration=duration
        task.work=work
        task.hability_1=hability_1
        task.hability_2=hability_2
        task.recomend_username=recomend_username

        db.session.add(task)
        db.session.commit()

        return task
    @classmethod
    def update_start_and_finish(cls, id, order):
        task=Task.get_by_id(id)

        if task is None:
            return False
        if order==1:

            task.start=datetime.datetime.now()
            task.teoric_finish=datetime.datetime.now() + datetime.timedelta(days=task.duration)
        else:
            task.start=None
            task.teoric_finish=None

        db.session.add(task)
        db.session.commit()

        return task

    @classmethod
    def update_state(cls,id, state):
        task=Task.get_by_id(id)

        if task is None:
            return False

        task.state=state

        db.session.add(task)
        db.session.commit()

        return task

    @classmethod
    def update_user_id(cls,id, user_id):
        task=Task.get_by_id(id)

        if task is None:
            return False

        task.user_id=user_id

        db.session.add(task)
        db.session.commit()

        return task

    @classmethod
    def update_percent(cls,id, percent):
        task=Task.get_by_id(id)

        if task is None:
            return False

        task.percent=percent

        db.session.add(task)
        db.session.commit()

        return task

    @classmethod
    def set_concatenate(cls, id, precedent_task_id):
        task=Task.get_by_id(id)

        if task is None:
            return False

        task.precedent_task_id=precedent_task_id

        db.session.add(task)
        db.session.commit()

        return task


    @classmethod
    def delete_element(cls,id):
        task=Task.get_by_id(id)

        if task is None:
            return False

        db.session.delete(task)
        db.session.commit()

        return True

class Profile(db.Model):
    __tablename__='profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user= db.relationship('User', back_populates='profile')
    name= db.Column(db.String(20), nullable=False)
    last_name= db.Column(db.String(30), nullable=False)
    first_hab= db.Column(db.String(20), nullable=True)
    second_hab= db.Column(db.String(20),nullable=True)
    third_hab= db.Column(db.String(20), nullable=True)
    telephone= db.Column(db.String(15), nullable=True)
    email = db.Column(db.String(100),unique=True,nullable=False)

    @classmethod
    def create_element(cls, user_id , user , name, last_name, first_hab, second_hab, third_hab, telephone,email):
        profile= Profile(user_id= user_id, user= user, name=name, last_name=last_name, first_hab=first_hab,
                         second_hab=second_hab, third_hab=third_hab, telephone=telephone, email=email)

        db.session.add(profile)
        db.session.commit()

        return profile

    @classmethod
    def get_by_user(cls, user):
        return Profile.query.filter_by(user=user).first()

    @classmethod
    def get_by_user_id(cls, user_id):
        return Profile.query.filter_by(user_id=user_id).first()

    @classmethod
    def change_to_admin(cls,user_id):
        profile=Profile.get_by_user_id(user_id)

        if profile is None:
            return False

        profile.first_hab='0'
        profile.second_hab='0'
        profile.third_hab='0'

        db.session.add(profile)
        db.session.commit()

        return profile


    @classmethod
    def update_element(cls,user_id, user, name, last_name, first_hab, second_hab, third_hab, telephone, email):
        profile=Profile.get_by_user(user)

        if profile is None:
            return False

        profile.name=name
        profile.last_name=last_name
        profile.first_hab=first_hab
        profile.second_hab=second_hab
        profile.third_hab=third_hab
        profile.telephone=telephone
        profile.email=email

        db.session.add(profile)
        db.session.commit()

        return profile
'''
    @classmethod
    def type_user(cls, user):
        profile= Profile.get_by_user(user)
        if profile.first_hab=='' or profile.second_hab or
'''
class Idea(db.Model):
    __tablename__='ideas'

    id = db.Column(db.Integer, primary_key=True)
    creator_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    problem= db.Column(db.Text(), nullable=False)
    solution= db.Column(db.Text(), nullable=False)
    extra_info=db.Column(db.Text())
    state=db.Column(db.Integer)       #  3 --> decline     2--->Accept   4--> idea project
    creator_involv=db.Column(db.String(30)) #recommendedProjectManager/idea/recommendedProjectMaker/projectManager
    project= db.relationship('Project', back_populates='idea')
    project_id=  db.Column(db.Integer, db.ForeignKey('projects.id'))

    @property
    def little_problem(self):
        if len(self.problem)>20:
            return self.problem[0:19]+'...'
        return self.problem
    @property
    def little_solution(self):
        if len(self.solution)>20:
            return self.solution[0:19]+'...'
        return self.solution
    @property
    def little_extra_info(self):
        if len(self.extra_info)>20:
            return self.extra_info[0:19]+'...'
        return self.extra_info


    @classmethod
    def create_element(cls, user_id,problem, solution, extrainfo, involvement, project_id):
        idea= Idea(creator_user_id= user_id, problem= problem, solution=solution, extra_info=extrainfo, creator_involv=involvement, project_id=project_id)

        db.session.add(idea)
        db.session.commit()

        return idea
    @classmethod
    def get_by_user_id(cls, user_id):
        return Idea.query.filter_by(creator_user_id=user_id).first()

    @classmethod
    def get_by_id(cls, id):
        return Idea.query.filter_by(id=id).first()

    @classmethod
    def delete_element(cls,id):
        idea=Idea.get_by_id(id)

        if idea is None:
            return False

        db.session.delete(idea)
        db.session.commit()

        return True

    @classmethod
    def update_state(cls, id, state):
        idea=Idea.get_by_id(id)

        if idea is None:
            return False

        idea.state=state

        db.session.add(idea)
        db.session.commit()

        return idea

    @classmethod
    def update_creator_involv(cls, id, involv):
        idea=Idea.get_by_id(id)

        if idea is None:
            return False

        idea.creator_involv=involv

        db.session.add(idea)
        db.session.commit()

        return idea

    @classmethod
    def update_project_id(cls, id, project_id):
        idea=Idea.get_by_id(id)
        if idea is None:
            return False
        idea.project_id=project_id

        db.session.add(idea)
        db.session.commit()

        return idea

    def __str__(self):
        return self.solution

class Project(db.Model):
    __tablename__='projects'
    id = db.Column(db.Integer, primary_key=True)
    ceo_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    manager_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recommended_manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    idea=db.relationship('Idea' , uselist=False, back_populates='project')
    title= db.Column(db.String(20),nullable=False)
    atractive_description=db.Column(db.Text(),nullable=False)
    description= db.Column(db.Text(),nullable=False)
    gen_obj_F1=db.Column(db.Text())
    work_percent_F1=db.Column(db.Integer)
    current_percent_F1=db.Column(db.Integer)
    gen_obj_F2=db.Column(db.Text())
    work_percent_F2=db.Column(db.Integer)
    current_percent_F2=db.Column(db.Integer)
    gen_obj_F3=db.Column(db.Text())
    work_percent_F3=db.Column(db.Integer)
    current_percent_F3=db.Column(db.Integer)
    tasks_project=  db.relationship('Task', lazy='dynamic')
    current_fase=  db.Column(db.Integer)
    edit_current_fase=  db.Column(db.Integer)
    reserve=db.Column(db.Float)
    num_fases=db.Column(db.Integer,nullable=False)
    members_com_secret= db.relationship('Comercial_secret', lazy='dynamic')
    presentation_id= db.Column(db.Integer, db.ForeignKey('files.id'))
    ceo_key=db.Column(db.String(20))
    secured_key=db.Column(db.Integer)
    current_actions= db.Column(db.Float)
    top_demand = db.Column(db.Float)
    our_percent= db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    start_at = db.Column(db.DateTime)
    teoric_finish = db.Column(db.DateTime, default=None)
    hide = db.Column(db.Integer)


    @property
    def little_description(self):
        if len(self.description)>20:
            return self.description[0:19]+'...'
        return self.description

    @property
    def little_title(self):
        if len(self.title)>10:
            return self.title[0:9]+'...'
        return self.title

    @classmethod
    def update_start_and_finish(cls, id):
        project=Project.get_by_id(id)

        if project is None:
            return False

        project.start=datetime.datetime.now()
        project.teoric_finish=datetime.datetime.now() + datetime.timedelta(days=project.num_fases * 31)

        db.session.add(project)
        db.session.commit()

        return project

    @classmethod
    def clear_recommended_manager(cls, id):
        project=Project.get_by_id(id)
        if project is None:
            return False

        project.recommended_manager_id=None
        db.session.add(project)
        db.session.commit()

        return project

    @classmethod
    def create_element(cls, ceo_user_id,idea, title,
                        atractive_description, description, gen_obj_F1,percent_F1,
                        gen_obj_F2,percent_F2,gen_obj_F3, percent_F3, current_fase, reserve,
                        num_fases, edit_current_fase, ceo_key, secured_key, current_actions, top_demand, our_percent, recommended_manager_id, hide):
        if num_fases=='3':
            project= Project( ceo_user_id=ceo_user_id,title=title,atractive_description=atractive_description,
                            description=description,gen_obj_F1=gen_obj_F1,work_percent_F1=percent_F1,current_percent_F1= 100, gen_obj_F2=gen_obj_F2,
                            work_percent_F2=percent_F2, current_percent_F2= 100, gen_obj_F3=gen_obj_F3,work_percent_F3=percent_F3,current_percent_F3= 100,
                            current_fase=current_fase,reserve=reserve, num_fases=num_fases, edit_current_fase=edit_current_fase, ceo_key=ceo_key,
                            secured_key=secured_key, current_actions=current_actions,top_demand=top_demand, our_percent=our_percent , recommended_manager_id=recommended_manager_id, hide=hide)
        elif num_fases=='2':
            project= Project( ceo_user_id=ceo_user_id,title=title,atractive_description=atractive_description,
                            description=description,gen_obj_F1=gen_obj_F1,work_percent_F1=percent_F1, current_percent_F1= 100, gen_obj_F2=gen_obj_F2,
                            work_percent_F2=percent_F2,current_percent_F2= 100, current_fase=current_fase,reserve=reserve, num_fases=num_fases,
                            edit_current_fase=edit_current_fase, ceo_key=ceo_key,secured_key=secured_key,current_actions=current_actions, top_demand=top_demand, our_percent=our_percent, recommended_manager_id=recommended_manager_id, hide=hide)
        elif num_fases=='1':
            project= Project( ceo_user_id=ceo_user_id,
                            title=title,atractive_description=atractive_description,
                            description=description,gen_obj_F1=gen_obj_F1,work_percent_F1=percent_F1,current_percent_F1= 100,
                            current_fase=current_fase,reserve=reserve, num_fases=num_fases, edit_current_fase=edit_current_fase, ceo_key=ceo_key,
                            secured_key=secured_key, current_actions=current_actions, top_demand=top_demand , our_percent=our_percent, recommended_manager_id=recommended_manager_id, hide=hide)
        db.session.add(project)
        db.session.commit()
        return project
    @classmethod
    def update_manager_user_id(cls, project_id, manager_user_id):
        project= Project.get_by_id(project_id)
        if project is None:
            return False
        project.manager_user_id=manager_user_id
        db.session.add(project)
        db.session.commit()

        return project

    @classmethod
    def update_current_actions(cls, project_id, current_actions):
        project= Project.get_by_id(project_id)
        if project is None:
            return False
        project.current_actions=current_actions
        db.session.add(project)
        db.session.commit()

        return project


    @classmethod
    def update_hide(cls, project_id, hide):
        project= Project.get_by_id(project_id)
        if project is None:
            return False
        project.hide=hide
        db.session.add(project)
        db.session.commit()

        return project

    @classmethod
    def update_current_fase(cls, project_id, current_fase):
        project= Project.get_by_id(project_id)
        if project is None:
            return False
        project.current_fase=current_fase
        db.session.add(project)
        db.session.commit()

        return project

    @classmethod
    def update_reserve(cls, project_id, reserve):
        project= Project.get_by_id(project_id)
        if project is None:
            return False
        project.reserve=reserve
        db.session.add(project)
        db.session.commit()

        return project

    @classmethod
    def update_our_percent(cls, project_id, our_percent):
        project= Project.get_by_id(project_id)
        if project is None:
            return False
        project.our_percent=our_percent
        db.session.add(project)
        db.session.commit()

        return project

    @classmethod
    def update_description(cls, project_id, new_description):
        project= Project.get_by_id(project_id)
        if project is None:
            return False
        project.description=new_description
        db.session.add(project)
        db.session.commit()

        return project

    @classmethod
    def update_secured_key(cls,project_id,secured_key):
        project= Project.get_by_id(project_id)
        if project is None:
            return False
        project.secured_key=secured_key
        db.session.add(project)
        db.session.commit()

        return project

    @classmethod
    def update_atractive_description(cls, project_id, new_atractive_description):
        project= Project.get_by_id(project_id)
        if project is None:
            return False
        project.atractive_description=new_atractive_description
        db.session.add(project)
        db.session.commit()

        return project

    @classmethod
    def update_title(cls, project_id, title):
        project= Project.get_by_id(project_id)
        if project is None:
            return False
        project.title=title
        db.session.add(project)
        db.session.commit()

        return project
    @classmethod
    def update_current_percent_F1(cls,project_id, current_percent_F1):
        project= Project.get_by_id(project_id)
        if project is None:
            return False
        project.current_percent_F1=current_percent_F1
        db.session.add(project)
        db.session.commit()

        return project

    @classmethod
    def update_current_percent_F2(cls,project_id, current_percent_F2):
        project= Project.get_by_id(project_id)
        if project is None:
            return False
        project.current_percent_F2=current_percent_F2
        db.session.add(project)
        db.session.commit()

        return project

    @classmethod
    def update_edit_current_fase(cls,project_id, edit_current_fase):
        project= Project.get_by_id(project_id)
        if project is None:
            return False
        project.edit_current_fase=edit_current_fase
        db.session.add(project)
        db.session.commit()

        return project

    @classmethod
    def update_current_percent_F3(cls,project_id, current_percent_F3):
        project= Project.get_by_id(project_id)
        if project is None:
            return False
        project.current_percent_F3=current_percent_F3
        db.session.add(project)
        db.session.commit()

        return project

    @classmethod
    def update_presentation(cls,project_id,file_id):
        project= Project.get_by_id(project_id)
        if project is None:
            return False
        project.presentation_id=file_id
        db.session.add(project)
        db.session.commit()

        return project

    @classmethod
    def update_obj_per_1(cls,project_id, obj_1, percent_1):
        project= Project.get_by_id(project_id)
        if project is None:
            return False
        project.gen_obj_F1=obj_1
        project.work_percent_F1=percent_1
        db.session.add(project)
        db.session.commit()

        return project

    @classmethod
    def update_obj_per_2(cls,project_id, obj_2, percent_2, obj_1, percent_1):
        project= Project.get_by_id(project_id)
        if project is None:
            return False
        project.gen_obj_F2=obj_2
        project.work_percent_F2=percent_2
        project.gen_obj_F1=obj_1
        project.work_percent_F1=percent_1
        db.session.add(project)
        db.session.commit()

        return project

    @classmethod
    def update_obj_per_3(cls,project_id, obj_3, percent_3, obj_2, percent_2, obj_1, percent_1):
        project= Project.get_by_id(project_id)
        if project is None:
            return False
        project.gen_obj_F3=obj_3
        project.work_percent_F3=percent_3
        project.gen_obj_F2=obj_2
        project.work_percent_F2=percent_2
        project.gen_obj_F1=obj_1
        project.work_percent_F1=percent_1
        db.session.add(project)
        db.session.commit()

        return project

    @classmethod
    def get_by_id(cls , id):
        return Project.query.filter_by(id=id).first()

class Comercial_secret(db.Model):
    __tablename__='comercial_secrets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id= db.Column(db.Integer, db.ForeignKey('projects.id'),nullable=False)

    @classmethod
    def create_element(cls, user_id, project_id):
        com_secret= Comercial_secret(user_id=user_id, project_id=project_id)
        db.session.add(com_secret)
        db.session.commit()
        return com_secret

class Contract(db.Model):
    __tablename__='contracts'
    id= db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    percent = db.Column(db.Float)
    type= db.Column(db.String(20))
    project_percent=db.Column(db.Float)
    our_percent=db.Column(db.Float)
    reserve=db.Column(db.Float)
    state=db.Column(db.Integer) # 0--> not closed, 1--> on course, 2--> Done, 3--> Breaked

    @classmethod
    def create_element(cls,user_id, task_id, project_id, percent, project_percent, our_percent, reserve,type, state):
        contract= Contract( user_id=user_id ,task_id=task_id,project_id=project_id, percent=percent, type=type, project_percent=project_percent, our_percent=our_percent, reserve=reserve, state=state)
        db.session.add(contract)
        db.session.commit()
        return contract

    @classmethod
    def change_state(cls,contract_id, state):
        contract= Contract.get_by_id(contract_id)
        contract.state=state
        db.session.add(contract)
        db.session.commit()
        return contract

    @classmethod
    def delete_element(cls,id):
        contract=Contract.get_by_id(id)

        if contract is None:
            return False

        db.session.delete(contract)
        db.session.commit()

        return True

    @classmethod
    def get_by_id(cls , id):
        return Contract.query.filter_by(id=id).first()

class File(db.Model):
    __tablename__='files'
    id= db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(300),nullable=False)
    data= db.Column(db.LargeBinary,nullable=False)

    @classmethod
    def create_element(cls,file_data, file_name):
        file= File( name=file_name ,data=file_data)
        db.session.add(file)
        db.session.commit()
        return file

    @classmethod
    def download_element(cls,id):
        file= File.query.filter_by(id=id).first()
        return send_file(BytesIO(file.data), attachment_filename='DbEntry.txt', as_attachment=True)

    @classmethod
    def get_by_id(cls , id):
        return File.query.filter_by(id=id).first()
