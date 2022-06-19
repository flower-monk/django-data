from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from .forms import UserLoginForm, UserRegisterForm, ProfileForm
from .models import Profile
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def user_login(request):
    if request.method == 'POST':
        user_login_form = UserLoginForm(data=request.POST)
        if user_login_form.is_valid():
            # 清洗出合法数据
            data = user_login_form.cleaned_data
            # 检验账号、密码是否正确匹配数据库中的某个用户
            # 如果均匹配则返回这个 user 对象
            user = authenticate(username=data['username'], password=data['password'])
            if user:
                login(request, user)
                return redirect("wordpad:article_list")
            else:
                return HttpResponse("账户或密码输入有误。请检查重新输入~")
        else:
            return HttpResponse("账户和密码输入不合法")
    elif request.method == 'GET':
        user_login_form = UserLoginForm()
        context = { 'form': user_login_form }
        return render(request, 'userprofile/login.html', context)
    else:
        return HttpResponse("请使用GET或者POST请求数据")


def user_logout(request):
    logout(request)
    return redirect("wordpad:article_list")

def user_register(request):
    if request.method == 'POST':
        user_register_form = UserRegisterForm(data=request.POST)
        if user_register_form.is_valid():
            new_user = user_register_form.save(commit=False)
            new_user.set_password(user_register_form.cleaned_data['password'])
            new_user.save()
            login(request, new_user)
            return redirect("wordpad:article_list")
        else:
            return HttpResponse("注册表单输入有误，请重新输入")
    elif request.method == 'GET':
        user_register_form = UserRegisterForm()
        context = {'form': user_register_form}
        return render(request, 'userprofile/register.html', context)
    else:
        return HttpResponse("请使用GET或POST请求数据")


'''
@login_required是一个Python装饰器。装饰器可以在不改变某个函数内容的前提下，给这个函数添加一些功能。
具体来说就是@login_required要求调用user_delete()函数时，用户必须登录；如果未登录则不执行函数，
将页面重定向到/userprofile/login/地址去。
'''
@login_required(login_url='/userprofile/login/')
def user_delete(request, id):
    if request.method == 'POST':
        user = User.objects.get(id=id)
        if request.user == user:
            logout(request)
            user.delete()
            return redirect("wordpad:article_list")
        else:
            return HttpResponse("你没有删除操作的权限")
    else:
        return HttpResponse("仅接受REST请求")

@login_required(login_url='/userprofile/login/')
def profile_edit(request, id):
    user = User.objects.get(id=id)
    # profile = Profile.objects.get(user_id=id)
    if Profile.objects.filter(user_id=id).exists():
        profile = Profile.objects.get(user_id=id)
    else:
        profile = Profile.objects.create(user=user)

    if request.method == 'POST':
        if request.user != user:
            return HttpResponse("你没有权限修改此用户信息。")
        profile_form = ProfileForm(request.POST, request.FILES)
        if profile_form.is_valid():
            # 取得清洗后的合法数据
            profile_cd = profile_form.cleaned_data
            profile.phone = profile_cd['phone']
            profile.bio = profile_cd['bio']
            #表单上传的文件对象存储在类字典对象request.FILES中，因此需要修改表单类的参数，将它一并传递进去。
            if 'avatar' in request.FILES:
                # print("profile_cd: " + profile_cd)
                profile.avatar = profile_cd["avatar"]
            profile.save()
            # 带参数的 redirect()
            return redirect("userprofile:edit", id=id)
        else:
            return HttpResponse("注册表单输入有误。请重新输入~")
    elif request.method == 'GET':
        profile_form = ProfileForm()
        context = {'profile_form': profile_form, 'profile': profile, 'user': user}
        return render(request, 'userprofile/edit.html', context)
    else:
        return HttpResponse("请使用GET或POST请求数据")
