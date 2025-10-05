from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Max
from .models import Message


@login_required
def inbox(request):
    conversations = (
        Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user))
        .values('sender', 'receiver')
        .annotate(last_time=Max('timestamp'))
        .order_by('-last_time')
    )
    # Get unique partner ids
    partner_ids = set()
    for c in conversations:
        partner_id = c['receiver'] if c['sender'] == request.user.id else c['sender']
        partner_ids.add(partner_id)
    partners = User.objects.filter(id__in=partner_ids)
    return render(request, 'chat/inbox.html', {'partners': partners})


@login_required
def chat_view(request, username):
    partner = User.objects.get(username=username)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(sender=request.user, receiver=partner, content=content)
            return redirect('chat', username=partner.username)
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=partner) |
        Q(sender=partner, receiver=request.user)
    ).order_by('timestamp')
    return render(request, 'chat/chat.html', {'partner': partner, 'messages': messages})

# Create your views here.
