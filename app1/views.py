from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm, ProjectForm, MilestoneForm
from django.contrib.auth.decorators import login_required
from .models import Project, Milestone

from django.forms import inlineformset_factory, modelformset_factory
from django.shortcuts import get_object_or_404

from collections import Counter
from datetime import date

MilestoneFormSet = inlineformset_factory(
    Project,
    Milestone,
    form=MilestoneForm,
    extra=1,
    can_delete=True
)


def home(request):
    return render(request, 'home.html')


def features(request):
    return render(request, 'features.html') 


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(request, username=email, password=raw_password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Authentication failed.")
        else:
            messages.error(request, "Form is invalid.")
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def signin_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('dashboard')  # default after login
        else:
            return render(request, 'signin.html', {'error': 'Invalid credentials'})

    return render(request, 'signin.html')


@login_required(login_url='signin')
def dashboard_view(request):
    user = request.user
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    projects = Project.objects.filter(user=user)

    # Search filter
    if search_query:
        projects = projects.filter(title__icontains=search_query)

    # Status filter
    if status_filter:
        filtered_projects = []
        for project in projects:
            progress = project.progress
            if status_filter == 'not_started' and progress == 0:
                filtered_projects.append(project)
            elif status_filter == 'in_progress' and 0 < progress < 100:
                filtered_projects.append(project)
            elif status_filter == 'completed' and progress == 100:
                filtered_projects.append(project)
        projects = filtered_projects

    # Data for Project Status Doughnut Chart
    labels = ['Completed', 'In Progress', 'Not Started']
    completed = in_progress = not_started = 0

    for project in projects:
        p = project.progress
        if p == 100:
            completed += 1
        elif p == 0:
            not_started += 1
        else:
            in_progress += 1

    data = [completed, in_progress, not_started]

    # Data for Project Timeline Bar Chart
    project_titles = []
    project_days_left = []

    for project in projects:
        project_titles.append(project.title)
        if project.end_date:
            delta = (project.end_date - date.today()).days
            project_days_left.append(max(delta, 0))
        else:
            project_days_left.append(0)

    context = {
        'projects': projects,
        'search_query': search_query,
        'status_filter': status_filter,
        'labels': labels,
        'data': data,
        'project_titles': project_titles,
        'project_days_left': project_days_left
    }

    return render(request, 'dashboard.html', context)


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def create_project(request):
    MilestoneFormSet = modelformset_factory(Milestone, form=MilestoneForm, extra=0, can_delete=True)

    if request.method == 'POST':
        project_form = ProjectForm(request.POST)
        formset = MilestoneFormSet(request.POST, queryset=Milestone.objects.none())

        if project_form.is_valid() and formset.is_valid():
            project = project_form.save(commit=False)
            project.user = request.user
            project.save()

            for form in formset:
                milestone = form.save(commit=False)
                milestone.project = project
                milestone.save()
            return redirect('dashboard')
    else:
        project_form = ProjectForm()
        formset = MilestoneFormSet(queryset=Milestone.objects.none())

    return render(request, 'create_project.html', {
        'project_form': project_form,
        'formset': formset
    })


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    milestones = project.milestones.all()
    return render(request, 'project_detail.html', {
        'project': project,
        'milestones': milestones
    })


@login_required
def update_project(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    MilestoneFormSet = modelformset_factory(Milestone, form=MilestoneForm, extra=0, can_delete=True)

    if request.method == 'POST':
        project_form = ProjectForm(request.POST, instance=project)
        formset = MilestoneFormSet(request.POST, queryset=project.milestones.all())

        if project_form.is_valid() and formset.is_valid():
            project_form.save()
            milestones = formset.save(commit=False)

            for milestone in milestones:
                milestone.project = project
                milestone.save()

            for obj in formset.deleted_objects:
                obj.delete()

            return redirect('dashboard')

    else:
        project_form = ProjectForm(instance=project)
        formset = MilestoneFormSet(queryset=project.milestones.all())

    return render(request, 'update_project.html', {
        'project_form': project_form,
        'formset': formset,
        'project': project
    })

@login_required
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)

    if request.method == 'POST':
        project.delete()
        return redirect('dashboard')

    return render(request, 'delete_project_confirm.html', {'project': project})



@login_required
def toggle_milestone(request, pk):
    milestone = get_object_or_404(Milestone, pk=pk, project__user=request.user)
    if request.method == 'POST':
        milestone.is_completed = not milestone.is_completed
        milestone.save()
    return redirect('project_detail', pk=milestone.project.pk)

@login_required
def add_milestone(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = MilestoneForm(request.POST)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.project = project
            milestone.save()
            return redirect('project_detail', pk=project.pk)
    else:
        form = MilestoneForm()

    return render(request, 'add_milestone.html', {'form': form, 'project': project})


@login_required
def update_milestone(request, pk):
    milestone = get_object_or_404(Milestone, pk=pk, project__user=request.user)
    
    if request.method == 'POST':
        form = MilestoneForm(request.POST, instance=milestone)
        if form.is_valid():
            form.save()
            return redirect('project_detail', pk=milestone.project.pk)
    else:
        form = MilestoneForm(instance=milestone)

    return render(request, 'update_milestone.html', {'form': form, 'milestone': milestone})


@login_required
def delete_milestone(request, pk):
    milestone = get_object_or_404(Milestone, pk=pk, project__user=request.user)
    project_id = milestone.project.id
    if request.method == 'POST':
        milestone.delete()
        messages.success(request, "Milestone deleted.")
        return redirect('project_detail', pk=project_id)

    return render(request, 'delete_milestone_confirm.html', {'milestone': milestone})

@login_required
def toggle_milestone_completion(request, pk):
    milestone = get_object_or_404(Milestone, pk=pk, project__user=request.user)
    if request.method == 'POST':
        milestone.is_completed = not milestone.is_completed
        milestone.save()
    return redirect('project_detail', pk=milestone.project.id)

