import json

import markdown
from django.contrib.auth.models import User
from random import randrange

from django.db.models import Q
from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from .forms import ArticlePostForm
from .models import ArticlePost, ArticleColumn

from pyecharts import options as opts
from pyecharts.charts import Bar

from rest_framework.views import APIView
from django.core.paginator import Paginator

from django.views.generic import DetailView
from django.views.generic import ListView



# Create your views here.
def response_as_json(data):
    json_str = json.dumps(data)
    response = HttpResponse(
        json_str,
        content_type="application/json",
    )
    response["Access-Control-Allow-Origin"] = "*"
    return response


def json_response(data, code=200):
    data = {
        "code": code,
        "msg": "success",
        "data": data,
    }
    return response_as_json(data)


def json_error(error_string="error", code=500, **kwargs):
    data = {
        "code": code,
        "msg": error_string,
        "data": {}
    }
    data.update(kwargs)
    return response_as_json(data)


JsonResponse = json_response
JsonError = json_error

def bar_base() -> Bar:
    c = (
        Bar()
        .add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"])
        .add_yaxis("商家A", [randrange(0, 100) for _ in range(6)])
        .add_yaxis("商家B", [randrange(0, 100) for _ in range(6)])
        .set_global_opts(title_opts=opts.TitleOpts(title="Bar-基本示例", subtitle="我是副标题"))
        .dump_options_with_quotes()
    )
    return c

class ChartView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(bar_base()))

class IndexView(APIView):
    def get(self, request, *args, **kwargs):
        return render(request, 'wordpad/chart.html')

def article_delete(request, id):
    article = ArticlePost.objects.get(id=id)
    article.delete()
    return redirect("wordpad:article_list")


def article_safe_delete(request, id):
    if request.method == 'POST':
        article = ArticlePost.objects.get(id=id)
        article.delete()
        return redirect("wordpad:article_list")
    else:
        return HttpResponse("仅允许post请求")


def article_update(request, id):
    article = ArticlePost.objects.get(id=id)
    # 过滤非作者的用户
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")
    if request.method == "POST":
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            article.title = request.POST['title']
            article.body = request.POST['body']
            if request.POST['column'] != 'none':
                article.column = ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column = None

            if request.FILES.get('avatar'):
                article.avatar = request.FILES.get('avatar')

            article.tags.set(*request.POST.get('tags').split(','), clear=True)
            article.save()
            return redirect("wordpad:article_detail", id=id)
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    else:
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        context = {
            'article': article,
            'article_post_form': article_post_form,
            'columns': columns,
            'tags': ','.join([x for x in article.tags.names()]),
        }
        return render(request, 'wordpad/update.html', context)


def article_create(request):
    if request.method == "POST":
        article_post_form = ArticlePostForm(request.POST, request.FILES)
        if (article_post_form.is_valid()):
            new_article = article_post_form.save(commit=False)
            new_article.author = User.objects.get(id=request.user.id)
            # 新增的代码
            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            new_article.save()
            article_post_form.save_m2m()
            return redirect("wordpad:article_list")
        else:
            return HttpResponse("表单信息有误，请重新填写。")
    else:
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        context = {'article_post_form': article_post_form, 'columns': columns}
        return render(request, 'wordpad/create.html', context)

class ArticleListView(ListView):
    context_object_name = 'articles'
    queryset = ArticlePost.objects.all()
    template_name = 'wordpad/list.html'

def article_list(request):
    # 从 url 中提取查询参数
    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')

    article_list = ArticlePost.objects.all()

    # 搜索查询集
    if search:
        article_list = article_list.filter(
            Q(title__icontains=search) |
            Q(body__icontains=search)
        )
    else:
        search = ''

    # 栏目查询集
    if column is not None and column.isdigit():
        article_list = article_list.filter(column=column)

    #标签查询集
    if tag and tag != 'None':
        article_list = article_list.filter(tags__name__in=[tag])

    # 查询集排序
    if order == 'total_views':
        article_list = article_list.order_by('-total_views')

    ####分页 开始####
    # 每页显示 1 篇文章
    paginator = Paginator(article_list, 3)
    # 获取 url 中的页码
    page = request.GET.get('page')
    # 将导航对象相应的页码内容返回给 articles
    articles = paginator.get_page(page)
    ####分页 结束####

    context = {
        'articles': articles,
        'order': order,
        'search': search,
        'column': column,
        'tag': tag,
    }

    return render(request, 'wordpad/list.html', context)


# class ArticleDetailView(DetailView):
#     queryset = ArticlePost.objects.all()
#     context_object_name = 'article'
#     template_name = 'wordpad/detail.html'
#
#     def get_object(self):
#         obj = super(ArticleDetailView, self).get_object()
#         obj.total_views += 1
#         obj.save(update_fields=['total_views'])
#         obj.body = markdown.markdown(obj.body,
#                                      extensions=['markdown.extensions.extra',
#                                                  'markdown.extensions.codehilite'])
#         return obj

def article_detail(request, id):
    article = ArticlePost.objects.get(id=id)
    article.total_views += 1
    article.save(update_fields=['total_views'])
    article.body = markdown.markdown(article.body,
                                     extensions=['markdown.extensions.extra',
                                                 'markdown.extensions.codehilite'])
    context = {"article": article}
    return render(request, 'wordpad/detail.html', context)
