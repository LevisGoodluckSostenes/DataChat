from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django import forms
from .models import Story, Like, Comment, Category, Reply
from django.db.models import Prefetch


class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['title', 'description', 'file', 'category']


def home_view(request):
    stories = (
        Story.objects.select_related('author', 'author__profile', 'category')
        .order_by('-created_at')
    )
    return render(request, 'home.html', {'stories': stories})


def story_detail(request, pk):
    story = get_object_or_404(Story.objects.select_related('author', 'author__profile', 'category'), pk=pk)
    comments_qs = (
        Comment.objects.filter(story=story)
        .select_related('user', 'user__profile')
        .prefetch_related(Prefetch('replies', queryset=Reply.objects.select_related('user', 'user__profile')))
        .order_by('-created_at')
    )
    comments = comments_qs
    liked = False
    if request.user.is_authenticated:
        liked = story.likes.filter(user=request.user).exists()
    return render(request, 'stories/story_detail.html', {'story': story, 'comments': comments, 'liked': liked})


@login_required
def upload_story(request):
    if request.method == 'POST':
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.author = request.user
            obj.save()
            messages.success(request, 'Story uploaded successfully!')
            return redirect('home')
    else:
        form = StoryForm()
    return render(request, 'stories/upload_story.html', {'form': form})


@login_required
def toggle_like(request, pk):
    story = get_object_or_404(Story, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, story=story)
    liked = True
    if not created:
        like.delete()
        liked = False

    # If AJAX, return JSON; otherwise redirect back to detail
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'count': story.likes.count()})
    return redirect('story_detail', pk=pk)


@login_required
def add_comment(request, pk):
    if request.method != 'POST':
        return HttpResponseForbidden()
    story = get_object_or_404(Story, pk=pk)
    text = request.POST.get('text', '').strip()
    if text:
        Comment.objects.create(user=request.user, story=story, text=text)
    return redirect('story_detail', pk=pk)


@login_required
def add_reply(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            Reply.objects.create(comment=comment, user=request.user, text=text)
        return redirect('story_detail', pk=comment.story.pk)
    return render(request, 'stories/add_reply.html', {'comment': comment})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.user_id != request.user.id:
        return HttpResponseForbidden()
    story_pk = comment.story.pk
    comment.delete()
    return redirect('story_detail', pk=story_pk)


@login_required
def delete_reply(request, reply_id):
    reply = get_object_or_404(Reply, pk=reply_id)
    if reply.user_id != request.user.id:
        return HttpResponseForbidden()
    story_pk = reply.comment.story.pk
    reply.delete()
    return redirect('story_detail', pk=story_pk)


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.user_id != request.user.id:
        return HttpResponseForbidden()
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            comment.text = text
            comment.save()
            return redirect('story_detail', pk=comment.story.pk)
    return render(request, 'stories/edit_comment.html', {'comment': comment})


@login_required
def edit_reply(request, reply_id):
    reply = get_object_or_404(Reply, pk=reply_id)
    if reply.user_id != request.user.id:
        return HttpResponseForbidden()
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            reply.text = text
            reply.save()
            return redirect('story_detail', pk=reply.comment.story.pk)
    return render(request, 'stories/edit_reply.html', {'reply': reply})

# Create your views here.
