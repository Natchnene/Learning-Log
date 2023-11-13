from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.http import Http404

from .models import Topic, Entry
from .forms import TopicForm, EntryForm


def check_topic_owner(request, topic):
    if topic.owner != request.user:
        raise Http404


def index(request):
    """Home page of the application Learning log"""
    return render(request, 'learning_logs/index.html')


@login_required
def topics(request):
    """Gives a list of topics"""
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics}
    return render(request, 'learning_logs/topics.html', context)


@login_required
def topic(request, topic_id):
    """Gives one topic and all entries"""
    topic = Topic.objects.get(id=topic_id)
    check_topic_owner(request, topic)
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)


@login_required
def new_topic(request):
    """Defining a new topic"""
    if request.method != 'POST':
        # New topic doesn't send; creates a blank form
        form = TopicForm()
    else:
        # Sent data POST; process data
        form = TopicForm(data=request.POST)
        if form.is_valid:
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return HttpResponseRedirect(redirect_to='/topics')
    # Print a blank form or an invalid form
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)


@login_required
def new_entry(request, topic_id):
    """Adds a new entry on a specific topic"""
    topic = Topic.objects.get(id=topic_id)
    check_topic_owner(request, topic)
    if request.method != 'POST':
        # Data is not being sent; creates a blank form
        form = EntryForm()
    else:
        # Data POST sent; process data
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('learning_logs:topic', topic_id=topic_id)
    # Print a blank form or an invalid form
    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)


@login_required
def edit_entry(request, entry_id):
    """Edits an existing entry"""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    check_topic_owner(request, topic)
    if request.method != 'POST':
        # Initial query; the form is filled with data of te current entry
        form = EntryForm(instance=entry)
    else:
        # Sends data POST; process data
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)
    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)

