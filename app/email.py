from threading import Thread
from flask_mail import Message
from flask import current_app, render_template

from . import mail, app
def send_async_mail(message):
    with app.app_context():
        mail.send(message)

def welcome_mail(user):
    message= Message('Bienvenido a Investalent',
                        sender= current_app.config['MAIL_USERNAME'],
                        recipients= [user.email])

    message.html= render_template('email/welcome.html', user=user)
    thread=Thread(target=send_async_mail, args=[message])
    thread.start()

def project_manager_recommendation_mail(user, project):
    message= Message('Invitación a dirigir un proyecto con Investalent',
                        sender= current_app.config['MAIL_USERNAME'],
                        recipients= [user.email])

    message.html= render_template('email/project_recommendation.html', user=user, project=project, local_server= current_app.config['LOCAL_SERVER'])
    thread=Thread(target=send_async_mail, args=[message])
    thread.start()

def devel_recommendation_mail(user, task):
    message= Message('Invitación a desarrollar una tarea con Investalent',
                        sender= current_app.config['MAIL_USERNAME'],
                        recipients= [user.email])

    message.html= render_template('email/task_recommendation.html', user=user, task=task, local_server= current_app.config['LOCAL_SERVER'])
    thread=Thread(target=send_async_mail, args=[message])
    thread.start()

def work_finished_mail(user, project_manager, task):
    message= Message('Is the milestrone from '+ user.username + ' finished?',
                        sender= current_app.config['MAIL_USERNAME'],
                        recipients= [project_manager.email])
    message.html= render_template('email/work_finished.html', user=user, project_manager=project_manager, task=task, local_server= current_app.config['LOCAL_SERVER'])
    thread=Thread(target=send_async_mail, args=[message])
    thread.start()


def new_apply_mail(user, project_manager, task, project):
    message= Message('There is a new apply in your project',
                        sender= current_app.config['MAIL_USERNAME'],
                        recipients= [project_manager.email])
    message.html= render_template('email/new_apply_mail.html', user=user, project_manager=project_manager, task=task,project=project, local_server= current_app.config['LOCAL_SERVER'])
    thread=Thread(target=send_async_mail, args=[message])
    thread.start()

def new_contract_mail(user, project_manager, task, project):
    message= Message('Your have been selected for our project',
                        sender= current_app.config['MAIL_USERNAME'],
                        recipients= [user.email])
    message.html= render_template('email/new_contract_mail.html', user=user, project_manager=project_manager, task=task,project=project, local_server= current_app.config['LOCAL_SERVER'])
    thread=Thread(target=send_async_mail, args=[message])
    thread.start()

def new_project_manager_mail( project_manager):
    message= Message('We have selected you as project manager',
                        sender= current_app.config['MAIL_USERNAME'],
                        recipients= [project_manager.email])
    message.html= render_template('email/new_project_manager_mail.html', project_manager=project_manager)
    thread=Thread(target=send_async_mail, args=[message])
    thread.start()


def creator_recommendation_task_mail(user, task, project):
    message= Message('Invitación a desarrollar una tarea con Investalent',
                        sender= current_app.config['MAIL_USERNAME'],
                        recipients= [user.email])

    message.html= render_template('email/creator_task_recommendation.html', user=user, task=task, project=project, local_server= current_app.config['LOCAL_SERVER'])
    thread=Thread(target=send_async_mail, args=[message])
    thread.start()
