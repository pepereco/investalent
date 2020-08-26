from flask import Blueprint, send_file
from flask import render_template,request, flash, redirect, url_for, abort
from io import BytesIO
from flask_login import login_user, logout_user, login_required, current_user
from datetime import timedelta, datetime

from .forms import LoginForm, RegisterForm, TaskForm, ProfileForm, IdeaForm,SelectIdeaForm, NewProjectForm, SelectProjectPhase, SelectProjectTypeHab,Edit_title_project, Edit_description_project, Edit_atractive_description_project,Create_task, Edit_obj_per_1, Edit_obj_per_2, Edit_obj_per_3, Intro_project_key,SelectFindTask, SelectTaskPhase, SelectProjectPhaseAdmin, Select_all_task, SelectEvaluation, RecomendationTaskForm
from .models import User,Task, Profile, Idea, Project, Comercial_secret, File, Contract
from .email import welcome_mail, project_manager_recommendation_mail, work_finished_mail, devel_recommendation_mail, new_project_manager_mail, new_apply_mail, new_contract_mail, creator_recommendation_task_mail
from .import login_manager


page = Blueprint('page',__name__)

habilities_dict= {'1': 'None', '2':'Project Manager', '3':'UserType1', '4':'UserType2', '5':'UserType3'}

#######################################################################################################################

#parametros maximo tiempo recomendacion de usuarios
#maximo tiempo proj manager
max_days_recommended_pm=7
#maximo tiempo developer
max_days_recommended_devel=7



#Parametros calculo porcentaje hitos

top_demand= 1 # Numero de dias que passan per incrementar una unitat el valor de la demanda.
projectManagerPercent=0.2 # porcentaje sobre 1 que se lleva el proj manager

#Acciones por proyecto que se lleva Investalent
AccionesInvestalent=0.05
#fijoVsvar(F1) , determina la parte fija i variable del porcenatje,ademas de la posible parte que puede ir a reservas en funcion de la nota, quanto mas grande mas parte fija.(va de 0 a 1 (%))
#depende del trabajo
MinfijoVSvar=0.05
MaxfijoVSvar=0.15
fijoVSvar_1=0.5
fijoVSvar_2=0.6
fijoVSvar_3=0.7
#fase _2 , determina la minima parte que va a reservas proviniente de la parte variable, quanto mas grande menos % va a reservas.(va de 0 a 1 (%))
# depender de la fase
fase_1_2=0.8
fase_2_2=0.9
fase_3_2=1
#fase _3 , determina la rapidez del augmento del extra, quanto mas grande mas rapido, puede ser mayor a 1. (no %)
#depende de la fase
fase_1_3=0.75
fase_2_3=1
fase_3_3=1.25

#######################################################################################################################


@login_manager.user_loader
def load_user(id):
    return User.get_by_id(id)

@page.app_errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404

@page.route('/')
def index():
    return render_template('index.html',title='Index', active='home')



######Users######

@page.route('/login/<int:redirection_proj_id>/<int:redirection_task_id>', methods=['GET', 'POST'])
def login(redirection_proj_id, redirection_task_id):
    if current_user.is_authenticated and redirection_proj_id==0 and redirection_task_id == 0:
        return redirect(url_for('.index'))
    elif  current_user.is_authenticated:
        project=  Project.get_by_id(redirection_proj_id)
        task=  Task.get_by_id(redirection_task_id)
        if redirection_proj_id != 0 :
            if (project.recommended_manager_id==None or project.recommended_manager_id==current_user.id) and  (current_user.id != project.manager_user_id) :
                return redirect(url_for('.recommendation_projects', project_id=redirection_proj_id))
            elif current_user.id == project.manager_user_id:
                return redirect(url_for('.tasks_editor', project_id=project.id, show_phase=1))
        if redirection_task_id != 0 :
            if (task.recomend_username=='' or task.recomend_username==current_user.username) and (current_user.id != task.user_id) :
                return redirect(url_for('.recommendation_tasks', task_id=redirection_task_id))
            elif (current_user.id == task.user_id):
                return redirect(url_for('.my_tasks'))
            else:
                return redirect(url_for('.index'))

    form =LoginForm(request.form)
    if request.method=='POST' and form.validate():
        user= User.get_by_username(form.username.data)
        if user and user.verify_password(form.password.data):
            login_user(user)
            flash('User authentified')

            if current_user.is_authenticated and redirection_proj_id==0 and redirection_task_id == 0:
                return redirect(url_for('.index'))
            elif redirection_proj_id != 0:
                project=  Project.get_by_id(redirection_proj_id)
                if current_user.is_authenticated :
                    if (project.recommended_manager_id==None or project.recommended_manager_id==current_user.id) and current_user.id != project.manager_user_id:
                        return redirect(url_for('.recommendation_projects', project_id=redirection_proj_id))
                    elif current_user.id == project.manager_user_id:
                        return redirect(url_for('.tasks_editor', project_id=project.id, show_phase=1))

                    else:
                        return redirect(url_for('.index'))
            elif redirection_task_id != 0 :
                task=  Task.get_by_id(redirection_task_id)
                if (task.recomend_username=='' or task.recomend_username==current_user.username) and (current_user.id != task.user_id):
                    return redirect(url_for('.recommendation_tasks', task_id=redirection_task_id))
                elif (current_user.id == task.user_id):
                    return redirect(url_for('.my_tasks'))


        else:
            flash('Incorrect username or password', 'error')


    return render_template('auth/login.html', title='Login',form=form, active='login')

'''
@page.route('/tasks')
@page.route('/tasks/<int:page>')
@login_required
def tasks(page=1, per_page=2):
    pagination= current_user.tasks.paginate(page,per_page)
    tasks= pagination.items

    return render_template('task/list.html', title='Tareas', tasks=tasks,
                            pagination=pagination, page=page, active='tasks')

'''
@page.route('/create_admin')
@login_required
def create_admin():
    if current_user.profile == None:
        return redirect(url_for('.new_profile', admin='1'))
    else:
        Profile.change_to_admin(current_user.id)
        User.change_user_type(current_user.id, 3)
        flash('admin created')
        return redirect(url_for('.index'))

@page.route('/create_project_manager')
@login_required
def create_project_manager():
    if current_user.profile == None:
        return redirect(url_for('.new_profile', admin='2'))
    else:
        if (current_user.profile.first_hab!='1' and current_user.profile.first_hab!='2') or (current_user.profile.second_hab!='1' and current_user.profile.second_hab!='2') or (current_user.profile.third_hab!='1' and current_user.profile.third_hab!='2'):
            User.change_user_type(current_user.id, 4)
        else:
            User.change_user_type(current_user.id, 5)
        flash('solicitud enviada')
        return redirect(url_for('.index'))


@page.route('/return_to_developer')
@login_required
def return_to_developer():

    User.change_user_type(current_user.id, 1)
    flash('tipo de usuario canviado')
    return redirect(url_for('.index'))



@page.route('/logout')
def logout():
    logout_user()
    flash('You loged out')
    return redirect(url_for('.login', redirection_proj_id=0,  redirection_task_id=0))

@page.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('.index'))
    form = RegisterForm(request.form)

    if request.method=='POST':

        if form.validate():
            user= User.create_element(form.username.data, form.password.data, form.email.data)
            flash('User registred')
            login_user(user)
            welcome_mail(user)
            return redirect(url_for('.index'))
    return render_template('auth/register.html', title='Sign Up', form=form, active='register')

@page.route('/list_potential_pm')
@login_required
def list_potential_pm():
    potential_proj_manag_profiles=[]

    for user in User.query.all():
        if user.user_type == 4 or user.user_type == 5:
            potential_proj_manag_profiles.append(user.profile)

    return render_template('auth/proj_manag_selection.html', title='Project manager selection', potential_proj_manag_profiles=potential_proj_manag_profiles,
                            active='list_potential_pm')

@page.route('/select_project_manager/<selection>/<user_id>')
@login_required
def select_project_manager(selection, user_id):
    user= User.get_by_id(user_id)
    if selection=='accepted':
        if user.user_type== 0 or user.user_type == 4:
            User.change_user_type(user.id, 1)
        elif user.user_type == 5:
            User.change_user_type(user.id, 2)
        new_project_manager_mail(user)
    elif selection=='declined':
        User.change_user_type(user.id, 0)
    return redirect(url_for('.list_potential_pm'))

@page.route('/select_applier/<selection>/<int:contract_id>')
@login_required
def select_applier(selection, contract_id):
    contract= Contract.get_by_id(contract_id)
    task=Task.get_by_id(contract.task_id)
    if selection == 'accepted':
        return redirect(url_for('.sign_contract', task_id=contract.task_id, percent=contract.percent,porcentajeProyecto=contract.project_percent, AccEmp=contract.our_percent, reserva=contract.reserve, contract_id=contract.id ))
    elif selection=='declined':
        Contract.delete_element(contract_id)
        return redirect(url_for('.get_task', task_id=contract.task_id, project_id=task.project_id, show_phase=task.fase))






######Profiles######


@page.route('/profile/new/<admin>', methods= ['GET', 'POST'])
@login_required
def new_profile(admin):
    form= ProfileForm(request.form, email = current_user.email)
    if request.method == 'POST' and form.validate():
        if (form.first_hab.data==form.second_hab.data and form.first_hab.data!='1') or (form.first_hab.data==form.third_hab.data and form.first_hab.data!='1') or (form.third_hab.data== form.second_hab.data and form.second_hab.data!='1'):
            flash('Habilities can not be repeated')
        else:
            if form.email.data!=current_user.email:
                User.change_email(current_user.id, form.email.data)
            if admin=='1':
                profile=Profile.create_element(current_user.id, current_user,form.name.data,
                                                form.last_name.data, '0',       #0 is for admin
                                                '0', '0',
                                                form.telephone.data, form.email.data)
                User.change_user_type(current_user.id, 3)
                flash('Admin created')
            elif admin =='2':
                profile=Profile.create_element(current_user.id, current_user,form.name.data,
                                                form.last_name.data, form.first_hab.data,
                                                form.second_hab.data, form.third_hab.data,
                                                form.telephone.data, form.email.data)
                if (form.first_hab.data!='1' and form.first_hab.data!='2') or (form.second_hab.data!='1' and form.second_hab.data!='2') or (form.third_hab.data!='1' and form.third_hab.data!='2'):
                    User.change_user_type(current_user.id, 4)
                else:
                    User.change_user_type(current_user.id, 5)
                flash('Solicitud enviada')

            else:
                #first_hab=dict(form.first_hab.choices).get(form.first_hab.data)
                #second_hab=dict(form.second_hab.choices).get(form.second_hab.data)
                #third_hab=dict(form.third_hab.choices).get(form.third_hab.data)
                profile=Profile.create_element(current_user.id, current_user,form.name.data,
                                                form.last_name.data, form.first_hab.data,
                                                form.second_hab.data, form.third_hab.data,
                                                form.telephone.data, form.email.data)

                flash('Profile created')




            return redirect(url_for('.index'))

    return render_template('profile/new.html', title='Create profile', form=form, active= 'new_profile')


@page.route('/profile/edit/<profile_id>', methods= ['GET', 'POST'])
@login_required
def edit_profile(profile_id):
    profile=Profile.query.get_or_404(profile_id)

    if profile.user_id != current_user.id:
        abort(404)

    form=ProfileForm(request.form, obj=profile)
    if request.method=='POST' and form.validate():

        if form.email.data!=current_user.email:
            User.change_email(current_user.id, form.email.data)

        if (form.first_hab.data==form.second_hab.data and form.first_hab.data!='1') or (form.first_hab.data==form.third_hab.data and form.first_hab.data!='1') or (form.third_hab.data== form.second_hab.data and form.second_hab.data!='1'):
            flash('Habilities can not be repeated')
        else:
            #first_hab=dict(form.first_hab.choices).get(form.first_hab.data)
            #second_hab=dict(form.second_hab.choices).get(form.second_hab.data)
            #third_hab=dict(form.third_hab.choices).get(form.third_hab.data)
            profile= Profile.update_element(current_user.id, current_user,form.name.data,
                                            form.last_name.data, form.first_hab.data,
                                            form.second_hab.data, form.third_hab.data,
                                            form.telephone.data, form.email.data)

            flash('Profile edited')
            return redirect(url_for('.index'))
    return render_template('profile/edit.html', title='Edit profile', form=form, active = 'edit_profile')

@page.route('/profile/show/<username>/<int:contract_id>')
@login_required
def show_profile(username, contract_id):

    user=User.get_by_username(username)
    profile=user.profile

    return render_template('profile/show.html', title='Profile', profile=profile, user=user, contract_id=contract_id)


######Ideas######

@page.route('/new_idea', methods= ['GET', 'POST'])
@login_required
def new_idea():
    if current_user.profile==None:
        flash('First create a profile of contact')
        return redirect(url_for('.new_profile', admin='0'))
    if current_user.profile.first_hab == '2' or current_user.profile.second_hab == '2'or current_user.profile.third_hab == '2':
        form = IdeaForm(request.form, creator_involv='recommendedProjectManager')
    elif current_user.profile.first_hab != '1':
        form = IdeaForm(request.form, creator_involv='recommendedProjectMaker')
    else:
        form = IdeaForm(request.form, creator_involv='idea')

    if request.method =='POST' and form.validate():
        idea= Idea.create_element(current_user.id, form.problem.data, form.solution.data, form.extra_info.data, form.creator_involv.data, None)
        flash('We will investigate your idea')
        return redirect(url_for('.new_idea'))


    return render_template('idea/new.html', form=form, title='Project idea', active = 'new_idea')


@page.route('/idea/list_ideas/<type>/<change>', methods= ['GET', 'POST'])
@login_required
def list_ideas(type, change='0'):
    list_of_ideas=[]
    form= SelectIdeaForm(request.form, type=type)

    if (request.method=='POST'):
        change='0'

    if (request.method=='POST' and form.validate()) or change=='1':
        if change!='1':
            type=form.type.data

    for idea in Idea.query.all():
        if type=='1' and idea.state==None:
            list_of_ideas.append(idea)
        elif type=='2' and idea.state==2:
            list_of_ideas.append(idea)
        elif type=='3' and idea.state==3:
            list_of_ideas.append(idea)

    ideas= list_of_ideas
    return render_template('idea/list_ideas.html', title='Ideas', ideas=ideas,
                            type_form=type, active='list_ideas', form=form , change=change)


@page.route('/idea/get_idea/<idea_id>/<type>', methods= ['GET', 'POST'])
@login_required
def get_idea(idea_id, type):
    idea=Idea.query.get_or_404(idea_id)

    return render_template('idea/show.html', title='Idea', idea=idea, type=type)

@page.route('/idea/decline_idea/<idea_id>/<type>')
@login_required
def decline_idea(idea_id, type):
    Idea.update_state(idea_id,3)
    return redirect(url_for('.list_ideas',type=type, change='1' ))

@page.route('/idea/accept_idea/<idea_id>/<type>')
@login_required
def accept_idea(idea_id,type):
    Idea.update_state(idea_id,2)
    return redirect(url_for('.list_ideas',type=type, change='1'))



######Projects######

@page.route('/project/new/<idea_id>', methods= ['GET', 'POST'])
@login_required
def new_project(idea_id):

    form= NewProjectForm(request.form)
    idea=Idea.get_by_id(idea_id)
    creator=User.get_by_id(idea.creator_user_id)
    if idea.creator_involv=='recommendedProjectManager' and form.recomend_project_manager.data=='' and form.title.data == '':
        form.recomend_project_manager.data=creator.username
    if request.method == 'POST' and form.validate() and form.validate_sum_percent() and form.validate_recomend_project_manager(form.recomend_project_manager):
        if (creator.username != form.recomend_project_manager.data) and idea.creator_involv=='recommendedProjectManager':
            Idea.update_creator_involv(idea.id,'idea')

        if form.gen_obj_F1.data== 'stopValue':

            form.gen_obj_F1.data=''
            form.gen_obj_F2.data=''
            form.gen_obj_F3.data=''
            form.percent_F1.data=''
            form.percent_F2.data=''
            form.percent_F3.data=''

            return render_template('project/new.html', title='New Project', idea=idea, form=form, show_fases=True)
        else:
            if form.recomend_project_manager.data !='':
                recommended_manager= User.get_by_username(form.recomend_project_manager.data)
                recommended_manager_id= recommended_manager.id
            else:
                recommended_manager_id= None
            project=Project.create_element(current_user.id, idea,
                                            form.title.data, form.atractive_description.data, form.description.data,
                                            form.gen_obj_F1.data,form.percent_F1.data,
                                            form.gen_obj_F2.data,form.percent_F2.data,form.gen_obj_F3.data,
                                            form.percent_F3.data, 0, 0, form.num_fases.data, 0, form.ceo_key.data, 0 , 0 , top_demand , projectManagerPercent*AccionesInvestalent, recommended_manager_id, int(form.hide.data))

            if recommended_manager_id != None:
                try:
                    project_manager_recommendation_mail(recommended_manager, project)
                except:
                    flash("Error sending the project manager recommendation")

            Idea.update_project_id(idea.id, project.id)
            if form.ceo_key.data=='':
                Project.update_secured_key(project.id,1)
            Idea.update_state(idea.id,4)
            return redirect (url_for('.index' ))
    if request.method=='POST':
        flash ('Error introducing the data')
    return render_template('project/new.html', title='New Project', idea=idea, form=form, show_fases=False)


@page.route('/project/list_projects', methods= ['GET', 'POST'])
@login_required
def list_projects():
    list_of_projects=[]
    form= SelectProjectPhase(request.form)

    for project in Project.query.all():
        if ((datetime.now()-project.created_at).total_seconds())>(max_days_recommended_pm * 60*60*24) and project.recommended_manager_id !=None:
            Project.clear_recommended_manager(project.id)
        if (project.manager_user_id==None) and (project.recommended_manager_id ==None or project.recommended_manager_id==current_user.id) and project.hide==0:
            if form.state.data=='1' and project.current_fase==0 :
                list_of_projects.append(project)
            elif form.state.data=='2' and project.current_fase==1:
                list_of_projects.append(project)
            elif form.state.data=='3' and project.current_fase==2:
                list_of_projects.append(project)
            elif form.state.data=='4' and project.current_fase==3:
                list_of_projects.append(project)

    return render_template('project/list_projects.html', title='List of projects',
                            form=form, projects= list_of_projects, active='list_projects', admin=False)

@page.route('/project/list_all_projects', methods= ['GET', 'POST'])
@login_required
def list_all_projects():
    list_of_projects=[]
    form= SelectProjectPhaseAdmin(request.form)
    for project in Project.query.all():

        if form.project_searcher.data!='':
            if project.title == form.project_searcher.data:
                list_of_projects.append(project)
        else:
            if form.state.data=='1' and project.current_fase==0 :
                list_of_projects.append(project)
            elif form.state.data=='2' and project.current_fase==1:
                list_of_projects.append(project)
            elif form.state.data=='3' and project.current_fase==2:
                list_of_projects.append(project)
            elif form.state.data=='4' and project.current_fase==3:
                list_of_projects.append(project)
            elif form.state.data=='5':
                list_of_projects.append(project)

    return render_template('project/list_projects.html', title='List of projects',
                            form=form, projects= list_of_projects, active='list_all_projects', admin=True)

@page.route('/project/show/<project_id>', methods= ['GET', 'POST'])
@login_required
def show_project(project_id):
    formRecom=RecomendationTaskForm(request.form)
    Comercial_secret.create_element(current_user.id, project_id)
    project=Project.query.get_or_404(project_id)
    profile_ceo= Profile.get_by_user_id(project.ceo_user_id)
    profile_pm= Profile.get_by_user_id(project.manager_user_id)
    if request.method == 'POST':
        try:
            if formRecom.validate_recomend_user(formRecom.recomend_user) and formRecom.validate():
                user=User.get_by_username(formRecom.recomend_user.data)
                project_manager_recommendation_mail(user,project)
        except:
            flash('The username was incorrect, therefore no email has been send')


    return render_template('project/show.html', project=project, profile_ceo=profile_ceo, profile_pm=profile_pm, formRecom=formRecom)

@page.route('/project/hide_project/<project_id>/<int:hide>')
@login_required
def hide_project(project_id, hide):
    project=Project.update_hide(project_id, hide)
    return redirect(url_for('.show_project', project_id=project.id))


@page.route('/project/my_projects',methods= ['GET', 'POST'])
@login_required
def my_projects():
    list_of_projects=[]
    form= SelectProjectTypeHab(request.form)

    for project in Project.query.all():
        if form.typeHab.data=='1' and project.manager_user_id==current_user.id:
            list_of_projects.append(project)
        elif form.typeHab.data=='2' and project.idea.creator_user_id==current_user.id:
            list_of_projects.append(project)
        elif form.typeHab.data=='3' and project.ceo_user_id==current_user.id:
            list_of_projects.append(project)

    return render_template('project/my_projects.html', title='My projects',
                            form=form, projects= list_of_projects, active='my_projects')

@page.route('/project/start_my_project/<project_id>')
@login_required
def start_my_project(project_id):
    project= Project.update_manager_user_id(project_id, current_user.id)
    if project.recommended_manager_id == current_user.id:
        if current_user.user_type== 0 or current_user.user_type == 4:
            User.change_user_type(current_user.id, 1)
        elif current_user.user_type == 5:
            User.change_user_type(current_user.id, 2)
    Project.update_start_and_finish(project.id)
    Project.update_current_actions(project.id, project.current_actions+20)
    Contract.create_element(user_id=current_user.id, task_id=None,project_id=project.id, percent=projectManagerPercent, project_percent= projectManagerPercent, our_percent=0, reserve=0 , type='Commited', state=1)
    return redirect(url_for('.my_projects'))
'''
@page.route('/project/manage_project/<project_id>')
@login_required
def manage_project(project_id):
    project= Project.update_manager_user_id(project_id, current_user.id)
    profile_ceo= Profile.get_by_user_id(project.ceo_user_id)
    return render_template

'''
@page.route('/project/intro_project_key/<project_id>',methods= ['GET', 'POST'])
@login_required
def intro_project_key(project_id):
    project= Project.get_by_id(project_id)
    form= Intro_project_key(request.form)
    if request.method=='POST' and form.validate():
        if (project.ceo_key==form.key.data):
            flash('The key is right')
            Project.update_secured_key(project_id,1)
        else:
            flash('Error, the key is wrong')
        return redirect(url_for('.show_project', project_id= project_id))
    return render_template('project/intro_project_key.html', title='Key', form=form, project_id=project_id)


@page.route('/project/edit_description_project/<project_id>',methods= ['GET', 'POST'])
@login_required
def edit_description_project(project_id):
    project= Project.get_by_id(project_id)
    form= Edit_description_project(request.form, obj=project)
    if request.method=='POST' and form.validate():
        if (Project.update_description(project_id, form.description.data)):
            flash('Edited')
        else:
            flash('Error updating')
        return redirect(url_for('.show_project', project_id= project_id))
    return render_template('project/edit_description.html', title='Edit', form=form, project_id=project_id)

@page.route('/project/edit_atractive_description/<project_id>',methods= ['GET', 'POST'])
@login_required
def edit_atractive_description_project(project_id):
    project= Project.get_by_id(project_id)
    form= Edit_atractive_description_project(request.form, obj=project)
    if request.method=='POST' and form.validate():
        if (Project.update_atractive_description(project_id, form.atractive_description.data)):
            flash('Edited')
        else:
            flash('Error updating')
        return redirect(url_for('.show_project', project_id= project_id))
    return render_template('project/edit_atractive_description.html', title='Edit', form=form, project_id=project_id)

@page.route('/project/edit_title_project/<project_id>',methods= ['GET', 'POST'])
@login_required
def edit_title_project(project_id):
    project= Project.get_by_id(project_id)
    form= Edit_title_project(request.form, obj=project)
    if request.method=='POST' and form.validate():
        if (Project.update_title(project_id, form.title.data)):
            flash('Edited')
        else:
            flash('Error updating')
        return redirect(url_for('.show_project', project_id= project_id))
    return render_template('project/edit_title.html', title='Edit', form=form, project_id=project_id)

@page.route('/project/edit_objectives_and_percent_1/<project_id>/<project_edit_phase>',methods= ['GET', 'POST'])
@login_required
def edit_objectives_and_percent(project_id, project_edit_phase):

    project= Project.get_by_id(project_id)
    if project.num_fases==3:
        form= Edit_obj_per_3(request.form,obj=project)
    elif project.num_fases==2:
        form=Edit_obj_per_2(request.form,obj=project)
    elif project.num_fases==1:
        form=Edit_obj_per_1(request.form,obj=project)
    if request.method=='POST' and form.validate():
        if project.num_fases==3:
            if (int(form.work_percent_F2.data) + int(form.work_percent_F1.data)+ int(form.work_percent_F3.data)!=100):
                flash ('The sum must be 100')
                return render_template('project/edit_objectives_and_percent.html', title='Edit', form=form, project=project, project_edit_phase=project_edit_phase)
            else:
                if (Project.update_obj_per_3(project_id, form.gen_obj_F3.data, form.work_percent_F3.data, form.gen_obj_F2.data, form.work_percent_F2.data, form.gen_obj_F1.data, form.work_percent_F1.data)):
                    flash('Edited')
                else:
                    flash('Error updating')
        elif project.num_fases==2:
            if (int(form.work_percent_F2.data) + int(form.work_percent_F1.data)!=100):
                flash ('The sum must be 100')
                return render_template('project/edit_objectives_and_percent.html', title='Edit', form=form, project=project, project_edit_phase=project_edit_phase)
            else:
                if (Project.update_obj_per_2(project_id, form.gen_obj_F2.data, form.work_percent_F2.data, form.gen_obj_F1.data, form.work_percent_F1.data)):
                    flash('Edited')
                else:
                    flash('Error updating')
        elif project.num_fases==1:
            if (int(form.work_percent_F1.data)!=100):
                flash ('The sum must be 100')
                return render_template('project/edit_objectives_and_percent.html', title='Edit', form=form, project=project, project_edit_phase=project_edit_phase)
            else:
                if (project.update_obj_per_1(project_id, form.gen_obj_F1.data, form.work_percent_F1.data)):
                    flash('Edited')
                else:
                    flash('Error updating')
        return redirect(url_for('.show_project', project_id= project_id))
    return render_template('project/edit_objectives_and_percent.html', title='Edit', form=form, project=project, project_edit_phase=project_edit_phase)

@page.route('/show_project_devel/<project_id>')
@login_required
def show_project_devel(project_id):
    project = Project.get_by_id(project_id)
    profile_ceo= Profile.get_by_user_id(project.ceo_user_id)
    proj_manager= User.get_by_id(project.manager_user_id)
    return render_template('project/show_devel.html', project=project, profile_ceo=profile_ceo, proj_manager=proj_manager)


@page.route('/project/edit_objectives_and_percent_2/<project_id>',methods= ['GET', 'POST'])
@login_required
def edit_objectives_and_percent_2(project_id):
    project= Project.get_by_id(project_id)
    form= Edit_obj_per_2(request.form, obj=project)
    if request.method=='POST' and form.validate():
        if project.num_fases==3:
            if (int(form.work_percent_F2.data) + int(project.work_percent_F1)+ int(project.work_percent_F3)>100):
                flash ('The sum can not be bigger than 100')
                return redirect(url_for('.show_project', project_id= project_id))
        elif project.num_fases==2:
            if (int(form.work_percent_F2.data) + int(project.work_percent_F1)>100):
                flash ('The sum can not be bigger than 100')
                return redirect(url_for('.show_project', project_id= project_id))

        if (Project.update_obj_per_2(project_id, form.gen_obj_F2.data, form.work_percent_F2.data)):
            flash('Edited')
        else:
            flash('Error updating')
        return redirect(url_for('.show_project', project_id= project_id))
    return render_template('project/edit_objectives_and_percent_2.html', title='Edit', form=form, project_id=project_id)

@page.route('/project/edit_objectives_and_percent_3/<project_id>',methods= ['GET', 'POST'])
@login_required
def edit_objectives_and_percent_3(project_id):
    project= Project.get_by_id(project_id)
    form= Edit_obj_per_3(request.form, obj=project)
    if request.method=='POST' and form.validate():
        if project.num_fases==3:
            if (int(form.work_percent_F3.data) + int(project.work_percent_F2)+ int(project.work_percent_F3)>100):
                flash ('The sum can not be bigger than 100')
                return redirect(url_for('.show_project', project_id= project_id))


        if (Project.update_obj_per_3(project_id, form.gen_obj_F3.data, form.work_percent_F3.data)):
            flash('Edited')
        else:
            flash('Error updating')
        return redirect(url_for('.show_project', project_id= project_id))
    return render_template('project/edit_objectives_and_percent_3.html', title='Edit', form=form, project_id=project_id)

@page.route('/project/leave_project/<project_id>')
@login_required
def leave_project(project_id):
    project= Project.get_by_id(project_id)
    flash ('You leaved the project: '+ project.title)
    Project.update_manager_user_id(project_id, None)
    Project.update_current_actions(project.id, project.current_actions-20)
    Project.update_secured_key(project_id, 0)
    for contract in current_user.contracts:
        if contract.project_id==project.id:
            Contract.change_state(contract.id,3)
    return redirect(url_for('.my_projects'))

@page.route('/recommendation_projects/<project_id>')
def recommendation_projects(project_id):
    project = Project.get_by_id(project_id)
    if not current_user.is_authenticated :
        return redirect(url_for('.login', redirection_proj_id=project_id, redirection_task_id=0))
    elif (project.recommended_manager_id==None or project.recommended_manager_id==current_user.id):
        return redirect(url_for('.show_project', project_id=project_id))
    return redirect(url_for('.index'))



######Tasks######

@page.route('/done_task/<task_id>/<confirmation>')
def done_task(task_id, confirmation):
    task = Task.get_by_id(task_id)
    project=Project.get_by_id(task.project_id)
    if confirmation=='1':
        Task.update_state(task_id, 2)
    if not current_user.is_authenticated :
        return redirect(url_for('.login', redirection_proj_id=task.project_id, redirection_task_id=0))
    return redirect(url_for('.tasks_editor', project_id=project.id, show_phase=task.fase))


@page.route('/work_finished/<proj_manager_id>/<task_id>')
@login_required
def work_finished(proj_manager_id, task_id):
    proj_manager= User.get_by_id(proj_manager_id)
    task= Task.get_by_id(task_id)
    work_finished_mail(current_user, proj_manager, task)
    return redirect(url_for('.my_tasks'))


"""
@page.route('/send_work/<proj_manager_id>')
@login_required
def send_work(proj_manager_id):
    proj_manager= User.get_by_id(proj_manager_id)
    send_work_mail(current_user, proj_manager)
    return redirect(url_for('.index'))
"""


@page.route('/find_task/show/<task_id>')
def show_task(task_id):
    if not current_user.is_authenticated :
        flash('Login needed')
        return redirect(url_for('.login', redirection_proj_id=0,  redirection_task_id=0))
    elif current_user.profile==None:
        flash('The profile is needed for seeing the milestones')
        return redirect(url_for('.new_profile', admin='0'))
    task=Task.query.get_or_404(task_id)
    project_id = task.project_id
    project=Project.query.get_or_404(project_id)
    Comercial_secret.create_element(current_user.id, project_id)
    demanda = calculo_demanda(task)
    task_percent, porcentajeProyecto,AccEmp,reserva = calculoPorcentajeTasca(task, demanda)
    months= int(task.duration/31)
    days= int(task.duration%31)
    project_manager =  User.get_by_id(project.manager_user_id)
    project_manager_name= project_manager.profile.name
    project_manager_lastname= project_manager.profile.last_name
    file_id = project.presentation_id
    return render_template('task/show_task_finder.html', title= 'Milestone finder' ,habilities_dict=habilities_dict, task=task,
                            porcentajeProyecto=porcentajeProyecto, AccEmp=AccEmp, reserva=reserva,file_id= file_id, project = project,
                            task_percent= task_percent, months= months, days=days, project_manager_name= project_manager_name,
                            project_manager_lastname=project_manager_lastname)


@page.route('/find_task/show/sign_contract/<task_id>/<percent>/<porcentajeProyecto>/<AccEmp>/<reserva>/<contract_id>')
@login_required
def sign_contract(task_id, percent,porcentajeProyecto,AccEmp,reserva, contract_id):
    task = Task.get_by_id(task_id)
    project= Project.get_by_id(task.project_id)
    project_manager=User.get_by_id(project.manager_user_id)
    contract=Contract.change_state(contract_id,1)
    developer=User.get_by_id(contract.user_id)
    new_contract_mail(developer, project_manager, task, project)
    Project.update_reserve(project.id, project.reserve+float(reserva))
    Project.update_current_fase(project.id, task.fase)
    Project.update_current_actions(project.id, porcentajeProyecto)
    Project.update_our_percent(project.id, project.our_percent+float(AccEmp))
    Task.update_start_and_finish(task.id, 1)
    Task.update_state(task.id, 1)
    Task.update_percent(task.id, percent)
    Task.update_user_id(task.id, developer.id)
    return redirect(url_for('.get_task', task_id=task.id, project_id=task.project_id, show_phase=task.fase))



@page.route('/find_task/show/apply_task/<task_id>/<percent>/<porcentajeProyecto>/<AccEmp>/<reserva>')
@login_required
def apply_task(task_id, percent,porcentajeProyecto,AccEmp,reserva):
    task = Task.get_by_id(task_id)
    project= Project.get_by_id(task.project_id)
    project_manager=User.get_by_id(project.manager_user_id)
    contract=Contract.create_element(user_id=current_user.id, task_id=task_id,project_id=project.id, percent=percent, project_percent= porcentajeProyecto, our_percent=AccEmp, reserve=reserva , type=task.commitment, state=0)
    new_apply_mail(current_user, project_manager, task, project)

    return redirect(url_for('.find_task'))



def calculo_demanda(task):
    dif = (((datetime.now() - task.created_at).total_seconds())/(3600.0*24.0))
    project= Project.get_by_id(task.project_id)
    topeDemanda=project.top_demand
    demanda = dif / topeDemanda
    current_fase= project.current_fase
    if current_fase==1 or current_fase==0:
        return demanda*fase_1_3
    elif current_fase ==2:
        return demanda*fase_2_3
    elif current_fase == 3:
        return demanda*fase_3_3


def calculoPorcentajeTasca(task, demanda):
    project= Project.get_by_id(task.project_id)
    if not current_user.is_authenticated :
        note = 0.5
    else:
        note = current_user.note /10.
    pastReserve= project.reserve
    pastOurActions = project.our_percent
    projectAcc= project.current_actions
    current_fase= project.current_fase
    if current_fase == 1 or current_fase==0:
        F2=fase_1_2
        F3=fase_1_3
        work_fase  = project.current_percent_F1
    elif current_fase ==2:
        F2=fase_2_2
        F3=fase_2_3
        work_fase  = project.current_percent_F2
    elif current_fase == 3:
        F2=fase_3_2
        F3=fase_3_3
        work_fase  = project.current_percent_F3

    if task.work <= MinfijoVSvar*100:
        F1=fijoVSvar_3
    elif (MaxfijoVSvar*100)> task.work > (MinfijoVSvar*100):
        F1=fijoVSvar_2
    elif task.work >= (MaxfijoVSvar*100):
        F1=fijoVSvar_1
    task_work = task.work * ( 1 - projectManagerPercent)
    fijo=task_work*F1
    variable =task_work*(1-F1)*note*F2
    entradaReserva=task_work*(1.-F1)*((1.-F2)*note+(1.- note))
    reservaAnt=pastReserve+entradaReserva
    AccEmp=task_work*(AccionesInvestalent/(1-projectManagerPercent))
    extra= demanda * task_work * note * reservaAnt
    reserva= reservaAnt - (AccEmp + extra)
    if (reserva)<0:
        porcentajeTasca= fijo+variable+(reservaAnt-AccEmp)
        reserva = 0
    else:
        porcentajeTasca= fijo+variable+extra

    porcentajeProyecto= porcentajeTasca + projectAcc
    reserva_tasca=reserva-pastReserve
    return "{0:.2f}".format(porcentajeTasca), porcentajeProyecto, AccEmp, reserva_tasca






@page.route('/find_task', methods=['GET', 'POST'])
def find_task():
    form = SelectFindTask(request.form)
    hability=dict(form.SelectTask.choices).get(form.SelectTask.data)
    list_tasks = []
    list_tasks_match1 , list_tasks_match2, list_tasks_match3, list_tasks_match4, list_tasks_match5, list_tasks_match6=([] for i in range (6))
    list_tasks_match_all1= []
    list_tasks_match_all2= []


    for task in Task.query.all():
        #if ((datetime.now()-task.created_at).total_seconds())>(max_days_recommended_devel *60*60*24) and task.recomend_username !='':
        #    Task.clear_recommended_username(task.id)
        precedent_task=Task.get_by_id(task.precedent_task_id)
        list_contracts_task_id=[]
        for contract in current_user.contracts:
            list_contracts_task_id.append(contract.task_id)
        if  task.user_id == None  and (precedent_task == None or precedent_task.state == 2 )  and task.hide ==0 and task.id not in list_contracts_task_id:
            demanda = calculo_demanda(task)
            task_percent, porcentajeProyecto,AccEmp,reserva = calculoPorcentajeTasca(task, demanda)
            if not current_user.is_authenticated or current_user.profile == None:
                form.SelectTask.data='2'
            if form.SelectTask.data=='1':
                if (task.hability_1 == current_user.profile.first_hab) and (task.hability_2 == current_user.profile.second_hab) or (task.hability_2 == current_user.profile.first_hab) and (task.hability_1 == current_user.profile.second_hab):
                    list_tasks_match1.append([task,task_percent])
                elif (task.hability_1 == current_user.profile.first_hab):
                    list_tasks_match2.append([task,task_percent])
                elif (task.hability_1 == current_user.profile.second_hab):
                    list_tasks_match3.append([task,task_percent])
                elif (task.hability_2 == current_user.profile.first_hab):
                    list_tasks_match4.append([task,task_percent])
                elif (task.hability_2 == current_user.profile.second_hab):
                    list_tasks_match5.append([task,task_percent])
                elif (task.hability_1 == current_user.profile.third_hab) or (task.hability_2 == current_user.profile.third_hab) :
                    list_tasks_match6.append([task,task_percent])

            elif form.SelectTask.data=='2':
                list_tasks.append([task,task_percent])
            elif form.SelectTask.data=='3' or form.SelectTask.data=='4' or form.SelectTask.data=='5':
                if (task.hability_1 == hability):
                    list_tasks_match_all1.append([task,task_percent])
                elif (task.hability_2 == hability):
                    list_tasks_match_all2.append([task,task_percent])




    if form.SelectTask.data=='1':
        list_tasks = list_tasks_match1 + list_tasks_match2 + list_tasks_match3 + list_tasks_match4 + list_tasks_match5  + list_tasks_match6
    elif form.SelectTask.data=='3' or form.SelectTask.data=='4' or form.SelectTask.data=='5':
        list_tasks = list_tasks_match_all1 + list_tasks_match_all2

    return render_template('task/find_task.html', title= 'Milestone finder' , list_tasks=list_tasks, form=form, habilities_dict= habilities_dict)


@page.route('/list_all_tasks', methods=['GET', 'POST'])
@login_required
def list_all_tasks():
    form = Select_all_task(request.form)
    hability=dict(form.SelectTask.choices).get(form.SelectTask.data)
    list_tasks = []
    list_tasks_match_all1= []
    list_tasks_match_all2= []

    for task in Task.query.all():
        if task.percent==None:
            demanda = calculo_demanda(task)
            task_percent, porcentajeProyecto,AccEmp,reserva = calculoPorcentajeTasca(task, demanda)
        else:
            task_percent=task.percent
        if form.task_searcher.data!='':
            if task.title==form.task_searcher.data:
                list_tasks.append([task,task_percent])
        else:
            if form.SelectTask.data=='2':
                list_tasks.append([task,task_percent])
            elif form.SelectTask.data=='3' or form.SelectTask.data=='4' or form.SelectTask.data=='5':
                if (task.hability_1 == hability):
                    list_tasks_match_all1.append([task,task_percent])
                elif (task.hability_2 == hability):
                    list_tasks_match_all2.append([task,task_percent])
    if form.SelectTask.data=='3' or form.SelectTask.data=='4' or form.SelectTask.data=='5' and form.task_searcher.data=='':
        list_tasks = list_tasks_match_all1 + list_tasks_match_all2


    return render_template('task/find_task.html', title= 'Milestone finder' , list_tasks=list_tasks, form=form, habilities_dict= habilities_dict, active= list_all_tasks)

@page.route('/my_tasks',methods= ['GET', 'POST'])
@login_required
def my_tasks():
    list_of_tasks=[]
    form= SelectTaskPhase(request.form)

    for task in current_user.tasks:
        if form.SelectTaskPhase.data=='1' and task.state == 1:
            list_of_tasks.append(task)
        elif form.SelectTaskPhase.data=='2' and task.state == 2:
            list_of_tasks.append(task)

    return render_template('task/my_tasks.html', title='My tasks',
                            form=form, tasks= list_of_tasks, active='my_tasks', habilities_dict= habilities_dict)


@page.route('/tasks/show_task_developer/<int:task_id>', methods=['GET', 'POST'])
@login_required
def show_task_developer(task_id):
    form=SelectEvaluation(request.form)
    task=Task.get_by_id(task_id)
    project = Project.get_by_id(task.project_id)
    profile_ceo= Profile.get_by_user_id(project.ceo_user_id)
    proj_manager= User.get_by_id(project.manager_user_id)
    if request.method=='POST' and form.validate():
        User.change_note_by_id(project.manager_user_id, form.eval.data*2)
        return redirect(url_for('.work_finished', proj_manager_id= project.manager_user_id, task_id=task.id))
    return render_template('task/show_developer.html', title='Show task', task= task, active='my_tasks' , habilities_dict= habilities_dict, project=project, profile_ceo=profile_ceo , proj_manager=proj_manager, form = form)

@page.route('/tasks/leave_task/<task_id>')
@login_required
def leave_task(task_id):
    change_project_phase=True
    task=Task.leave_task(task_id)
    project=Project.get_by_id(task.project_id)
    for contract in task.applicants:
        if contract.state==1 and contract.user_id==current_user.id:
            Contract.change_state(contract.id, 3)
            Project.update_reserve(project.id, project.reserve - contract.reserve)
            for task_proj in project.tasks_project:
                if task_proj.fase>=task.fase:
                    change_project_phase=False
            if change_project_phase==True:
                Project.update_current_fase(project.id, task.fase-1)
            Project.update_current_actions(project.id, project.current_actions-contract.percent)
            Project.update_our_percent(project.id, project.our_percent-contract.our_percent)
            Task.update_start_and_finish(task.id, 0)
            Task.update_state(task.id, 0)
            Task.update_percent(task.id, 0)
            Task.update_user_id(task.id, None)
    if current_user.user_type== 0 or current_user.user_type== 4 or current_user.user_type== 5:
        return redirect(url_for('.my_tasks'))
    else:
        return redirect(url_for('.get_task', task_id=task.id, project_id=task.project_id, show_phase=task.fase))

@page.route('/hide_task/<task_id>/<int:hide>')
@login_required
def hide_task(task_id, hide):
    task= Task.get_by_id(task_id)
    Task.update_hide(task_id, hide)
    return redirect(url_for('.list_all_tasks'))

@page.route('/project/tasks_editor/<project_id>/<show_phase>')
@login_required
def tasks_editor(project_id, show_phase):

    project= Project.get_by_id(project_id)
    if int(show_phase)>project.num_fases:
        flash('Error with the phase to show')
        return redirect(url_for('.index'))
    tasks=[]
    if show_phase=='0':
        show_phase='1'
    for task in Task.query.all():
        if int(show_phase)==task.fase and task.project_id==int(project_id):
            tasks.append(task)
    task_list=[]
    for task in tasks:
        if not(task.precedent_task_id):
            task_list.append([1, task])
    copy_task_list=[]+task_list
    for index, task_list_1 in enumerate(task_list):
        print (task_list_1[1])
        for task in tasks:
            i=0
            if task_list_1[1].id==task.precedent_task_id:
                i+=1
                copy_task_list.insert(index+i, [2, task])
                for task2 in tasks:
                    x=0
                    if task.id==task2.precedent_task_id:
                        x+=1
                        copy_task_list.insert(index+i+x, [3, task2])
                        for task3 in tasks:
                            z=0
                            if task2.id==task3.precedent_task_id:
                                z+=1
                                copy_task_list.insert(index+i+x+z, [4, task3])


    return render_template('project/tasks_editor.html', title='Milestone editor',project=project, tasks= copy_task_list, show_phase=show_phase, hab_dict=habilities_dict)

@page.route('/project/create_task/<project_id>/<show_phase>/<concatenate_task_id>',methods= ['GET', 'POST'])
@login_required
def create_task(project_id, show_phase, concatenate_task_id):
    project= Project.get_by_id(project_id)
    form= Create_task(request.form)
    if request.method=='POST' and form.validate() and form.validate_recomend_user(form.recomend_user):
        if form.months.data=='4' and form.days.data>0:
            flash ('Time error, the duration exced the limit, 3 months')
            return render_template('task/create_task.html', form=form, project=project, show_phase=show_phase)
        elif form.months.data=='1' and form.days.data==0:
            flash ('Time error, no time specified')
            return render_template('task/create_task.html', form=form, project=project, show_phase=show_phase)

        duration= int((int(form.months.data)-1)*31+form.days.data)
        #first_hab=dict(form.hability_1.choices).get(form.hability_1.data)
        #second_hab=dict(form.hability_2.choices).get(form.hability_2.data)
        commitment_value= dict(form.commitment.choices).get(form.commitment.data)

        if form.hability_1.data==form.hability_2.data:
            flash ('Error, the habilities are the same')
            return render_template('task/create_task.html', form=form, project=project, show_phase=show_phase)

        if show_phase=='1':
            if form.work.data>project.current_percent_F1:
                flash ('Error the percent of work exced the limit, '+ str(project.current_percent_F1)+'%')
                return render_template('task/create_task.html', form=form, project=project, show_phase=show_phase)
            current_percent_F1=project.current_percent_F1-form.work.data
            Project.update_current_percent_F1(project_id=project_id, current_percent_F1=current_percent_F1)


        elif show_phase=='2':
            if form.work.data>project.current_percent_F2:
                flash ('Error the percent of work exced the limit, '+ str(project.current_percent_F2)+'%')
                return render_template('task/create_task.html', form=form, project=project, show_phase=show_phase)
            current_percent_F2=project.current_percent_F2-form.work.data
            Project.update_current_percent_F2(project_id=project_id, current_percent_F2=current_percent_F2)

        elif show_phase=='3':
            if form.work.data>project.current_percent_F3:
                flash ('Error the percent of work exced the limit, '+ str(project.current_percent_F3)+'%')
                return render_template('task/create_task.html', form=form, project=project, show_phase=show_phase)
            current_percent_F3=project.current_percent_F3-form.work.data
            Project.update_current_percent_F3(project_id=project_id, current_percent_F3=current_percent_F3)
        if project.edit_current_fase==None:
            Project.update_edit_current_fase(project_id=project_id, edit_current_fase=int(show_phase))
        elif project.edit_current_fase<int(show_phase):
            Project.update_edit_current_fase(project_id=project_id, edit_current_fase=int(show_phase))


        task=Task.create_element(title= form.title.data, description=form.description.data, duration=duration, state=0,
                            fase=show_phase, work= form.work.data, project_id=project_id, hability_1=form.hability_1.data,
                            hability_2=form.hability_2.data, recomend_username=form.recomend_user.data, commitment=commitment_value,
                            objectives=form.objectives.data, hide = 0)
        if concatenate_task_id!='0':
            return redirect(url_for('.concatenate_task', task_id=task.id, project_id=project_id, show_phase=show_phase, concatenate_task_id=concatenate_task_id))
        if task.recomend_username!='':
            recomended_devel= User.get_by_username(task.recomend_username)
            try:
                devel_recommendation_mail(recomended_devel, task)
            except: flash('Error sending the recommendation')
        if project.idea.creator_involv == 'recommendedProjectMaker':
            recomend_maker=User.get_by_id(project.idea.creator_user_id)
            creator_recommendation_task_mail(recomend_maker, task, project)

        return redirect(url_for('.tasks_editor', project_id= project_id, show_phase=show_phase, hab_dict=habilities_dict))
    return render_template('task/create_task.html', form=form, project=project, show_phase=show_phase)



@page.route('/tasks/delete/<int:task_id>/<project_id>/<show_phase>')
@login_required
def delete_task(task_id, project_id, show_phase):
    task=Task.query.get_or_404(task_id)
    project= Project.get_by_id(project_id)
    if project.manager_user_id != current_user.id:
        abort(404)

    if Task.delete_element(task.id):

        if show_phase=='1':
            current_percent_F1=project.current_percent_F1+task.work
            Project.update_current_percent_F1(project_id=project_id, current_percent_F1=current_percent_F1)

        elif show_phase=='2':
            current_percent_F2=project.current_percent_F2+task.work
            Project.update_current_percent_F2(project_id=project_id, current_percent_F2=current_percent_F2)

        elif show_phase=='3':
            current_percent_F3=project.current_percent_F3+task.work
            Project.update_current_percent_F3(project_id=project_id, current_percent_F3=current_percent_F3)

        flash('Task deleted')
    return redirect(url_for('.tasks_editor', project_id= project_id, show_phase=show_phase, hab_dict=habilities_dict))

@page.route('/tasks/concatenate/<int:task_id>/<project_id>/<show_phase>/<concatenate_task_id>')
@login_required
def concatenate_task(task_id, project_id, show_phase, concatenate_task_id):
    Task.set_concatenate(task_id, concatenate_task_id)
    flash ('Task concatenated')
    return redirect(url_for('.tasks_editor', project_id= project_id, show_phase=show_phase, hab_dict=habilities_dict))


@page.route('/tasks/show/<int:task_id>/<project_id>/<show_phase>',methods= ['GET', 'POST'])
@login_required
def get_task(task_id, project_id, show_phase):
    formEval=SelectEvaluation(request.form)
    formRecom=RecomendationTaskForm(request.form)
    task=Task.query.get_or_404(task_id)
    project= Project.get_by_id(project_id)
    months= int(task.duration/31)
    days=int(task.duration%31)
    precedent_task_id= task.precedent_task_id
    first_hab=habilities_dict.get(task.hability_1)
    second_hab=habilities_dict.get(task.hability_2)
    task_devel = User.get_by_id(task.user_id)
    precedent_task_title=None
    list_applicants=[]
    for contract in task.applicants:
        applicant_user= User.get_by_id(contract.user_id)
        list_applicants.append([applicant_user,contract])
    if precedent_task_id!=None:
        precedent_task= Task.query.get_or_404(precedent_task_id)
        precedent_task_title= precedent_task.title
    if request.method=='POST' and formEval.validate() and formRecom.recomend_user.data=='':
        User.change_note_by_id(task.user_id, formEval.eval.data*2)
        return redirect(url_for('.done_task', task_id=task.id, confirmation=1))
    elif request.method=='POST' :
        try:
            if formRecom.validate_recomend_user(formRecom.recomend_user) and formRecom.validate():
                user=User.get_by_username(formRecom.recomend_user.data)
                devel_recommendation_mail(user,task)
        except:
            flash('The username was incorrect, therefore no email has been send')

    return render_template('task/show.html', title='Task', task=task, list_applicants=list_applicants, project=project, task_devel=task_devel, months=months, days=days, show_phase=show_phase, precedent_task_title=precedent_task_title, first_hab=first_hab, second_hab=second_hab, formEval=formEval, formRecom=formRecom)




@page.route('/tasks/edit/<int:task_id>/<project_id>/<show_phase>', methods=['GET','POST'])
@login_required
def edit_task(task_id, project_id,show_phase):
    task=Task.query.get_or_404(task_id)
    project=Project.get_by_id(project_id)
    recomend_user_before_edit=task.recomend_username
    form=Create_task(request.form, obj=task, months=int(task.duration/31)+1, days=int(task.duration%31), hability_1=task.hability_1, hability_2=task.hability_2, recomend_user=task.recomend_username)
    if project.manager_user_id != current_user.id:
        abort(404)

    if request.method=='POST' and form.validate():
        if form.months.data=='4' and form.days.data>0:
            flash ('Time error, the duration exced the limit, 3 months')
            return render_template('task/edit.html', form=form, project=project, show_phase=show_phase, concatenate_task_id=task.precedent_task_id)

        duration= int((int(form.months.data)-1)*31+form.days.data)
        #first_hab=dict(form.hability_1.choices).get(form.hability_1.data)
        #second_hab=dict(form.hability_2.choices).get(form.hability_2.data)
        if show_phase=='1':
            if form.work.data>(project.current_percent_F1+task.work):
                flash ('Error the percent of work exced the limit, '+ str(project.current_percent_F1)+'%')
                return render_template('task/edit.html', form=form, project=project, show_phase=show_phase)
            current_percent_F1=project.current_percent_F1-(form.work.data-task.work)
            Project.update_current_percent_F1(project_id=project_id, current_percent_F1=current_percent_F1)

        elif show_phase=='2':
            if form.work.data>(project.current_percent_F2+task.work):
                flash ('Error the percent of work exced the limit, '+ str(project.current_percent_F2)+'%')
                return render_template('task/edit.html', form=form, project=project, show_phase=show_phase)
            current_percent_F2=project.current_percent_F2-(form.work.data-task.work)
            Project.update_current_percent_F2(project_id=project_id, current_percent_F2=current_percent_F2)

        elif show_phase=='3':
            if form.work.data>(project.current_percent_F3+task.work):
                flash ('Error the percent of work exced the limit, '+ str(project.current_percent_F3)+'%')
                return render_template('task/edit.html', form=form, project=project, show_phase=show_phase)
            current_percent_F3=project.current_percent_F3-(form.work.data-task.work)
            Project.update_current_percent_F3(project_id=project_id, current_percent_F3=current_percent_F3)

        task= Task.update_element(id=task_id,title= form.title.data, description=form.description.data, duration=duration,
                            work= form.work.data,  hability_1=form.hability_1.data,hability_2=form.hability_2.data, recomend_username=form.recomend_user.data)
        if task:
            flash('Task updated')
            if task.recomend_username!='' and recomend_user_before_edit!=task.recomend_username:
                recomended_devel= User.get_by_username(task.recomend_username)
                try:
                    devel_recommendation_mail(recomended_devel, task)
                except: flash('Error sending the recommendation')
        return redirect(url_for('.tasks_editor', project_id= project_id, show_phase=show_phase, hab_dict=habilities_dict))
    return render_template('task/edit.html', title='Edit task', form=form, project=project, show_phase=show_phase)

@page.route('/recommendation_tasks/<task_id>')
def recommendation_tasks(task_id):
    task = Task.get_by_id(task_id)
    if not current_user.is_authenticated :
        return redirect(url_for('.login', redirection_proj_id=0, redirection_task_id= task_id))
    elif current_user.user_type == 2 :
        return redirect(url_for('.index'))
    return redirect(url_for('.show_task', task_id=task.id))

######Files######

@page.route('/upload_presentation/<project_id>', methods=['GET','POST'])
def upload_presentation(project_id):
    return render_template('project/upload_presentation.html',title='Upload presentation', project_id=project_id)



@page.route('/upload/<project_id>', methods=['GET','POST'])
@login_required
def upload(project_id):
    file=request.files['inputFile']
    project= Project.get_by_id(project_id)
    new_file=File.create_element(file_name=file.filename, file_data=file.read())
    Project.update_presentation(project_id, new_file.id)
    return redirect(url_for('.show_project', project_id= project_id))

@page.route('/download/<file_id>')
def download(file_id):
    file= File.get_by_id(file_id)
    return send_file(BytesIO(file.data), attachment_filename=file.name, as_attachment=True)
