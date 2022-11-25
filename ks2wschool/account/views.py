from django.shortcuts import render, redirect, resolve_url
from django.contrib import auth
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from blog.models import *

from account.models import User
from account.forms import CreateUserForm, LoginUserForm, UpdateUserForm
from .tokens import account_activation_token


# Create your views here.

def login(request):
    if request.method == 'POST':
        form = LoginUserForm(request.POST)
        next = request.POST.get('next')
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = User.objects.get(email=email)
            # request.session['user'] = form.user_id                 
            if user.is_active:
                user = auth.authenticate(email=email, password=password)
                auth.login(request, user)
                if request.POST.get('next'):
                    return redirect(request.POST['next'])
                else:
                    return redirect('index')
            else:
                current_site = get_current_site(request) 
                message = render_to_string('account/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
                })
                mail_title = user.nickname + "님의 계정 활성화"
                mail_to = email
                mail = EmailMessage(mail_title, message, to=[mail_to])
                mail.send()
                return render(request, 'account/activation_info.html', {'email': email})
                
                # form.add_error('email', '계정을 활성화해주세요')            
    else:
        form = LoginUserForm()
        next = request.GET.get('next')
    return render(request, 'account/login.html', {'form': form , 'next': next})
    

def signup(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            # raw_password = form.cleaned_data.get('password1')
            current_site = get_current_site(request) 
            user = User.objects.get(email=email)
            message = render_to_string('account/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            mail_title = user.nickname + "님의 계정 활성화"
            mail_to = email
            email = EmailMessage(mail_title, message, to=[mail_to])
            email.send()
            return render(request, 'account/activation_info.html')
            # auth.login(request, user)
            # return redirect('index')
    else:
        form = CreateUserForm() 
    return render(request, 'account/signup.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExsit):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        auth.login(request, user)
        return redirect("index")
    else:
        return render(request, 'blog/index.html', {'error' : '계정 활성화 오류'})


def profile(request, nickname):
    user = get_object_or_404(User, nickname=nickname)
    classification = request.GET.get('class','')
    if classification == 'comment':
        collection_list = user.comment_set.all()
    elif classification == 'reply':
        collection_list = user.reply_set.all()
    elif classification == 'voter':
        collection_list = user.voter_post.all()
    else:
        collection_list = user.voter_post.all()
    return render(request, 'account/profile.html', {'author': user ,'collection_list':collection_list,'classification':classification})

@login_required(login_url='login')
def profile_update(request, nickname):
    user = get_object_or_404(User, nickname=nickname)
    if request.user != user:
        messages.error(request, '수정 권한이 없습니다.')
        return redirect('profile', nickname=nickname)
    if request.method == 'POST':
        form = UpdateUserForm(request.POST, instance=user)
        if form.is_valid():
            user.profile_image.delete()
            user = form.save(commit=False)
            # print(form.cleaned_data['profile_image'])
            for img in request.FILES.getlist('profile_image'):
                user.profile_image = img
            user.save()
            return redirect('profile', nickname=nickname)
    else:
        form = UpdateUserForm(instance=user)
    return render(request, 'account/profile_update.html', {'form': form})

@login_required(login_url='login')
def profile_delete(request, nickname):
    user = get_object_or_404(User, nickname=nickname)
    if request.user != user:
        messages.error(request, '삭제 권한이 없습니다.')
        return redirect('profile', nickname=nickname)
    user.delete()
    return redirect('index')

@login_required(login_url='login')
def follow(request,nickname):
    user = get_object_or_404(User,nickname=nickname)
    if user != request.user:
        if user.followers.filter(nickname = request.user.nickname).exists():
            user.followers.remove(request.user)
        else:
            user.followers.add(request.user)
    return redirect('profile', user.nickname)


@login_required(login_url='login')
def view_follow(request,nickname):
    user = get_object_or_404(User,nickname=nickname)
   
    if user != request.user:
        if user.followers.filter(nickname = request.user.nickname).exists():
            user.followers.remove(request.user)
        else:
            user.followers.add(request.user)
       
    sorting = request.GET.get('sort', '')
    if sorting == 'following':
        follow_list = user.followings.all()
    elif sorting == 'follower':
        follow_list = user.followers.all()
    else :
        follow_list = user.followings.all()
    return render(request,'account/follow.html',{'user':user
        ,'follow_list':follow_list,'sorting':sorting})
    
    
