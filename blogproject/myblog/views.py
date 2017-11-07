from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse
from .models import Post, Category, Tag
import markdown
from comments.forms import CommentForm

from django.views.generic import ListView,DetailView

from markdown.extensions.toc import TocExtension
from django.utils.text import slugify
from django.db.models import Q

# Create your views here.

# def index(request):
#     return HttpResponse("欢迎访问我的博客首页")

# def index(request):
#    post_list = Post.objects.all().order_by('-created_time')
#    return render(request,'myblog/index.html',context={'post_list':post_list})


# def detail(request,pk):
#    post = get_object_or_404(Post,pk=pk)
#    # 调用一次阅读量+1
#    post.increase_views()
#    post.body = markdown.Markdown(post.body,
#                                  extensions=['markdown.extensions.extra',
#                                              'markdown.extensions.codehilite',
#                                              'markdown.extensions.toc',
#                                              ])
#    form = CommentForm()
#    # 获取全部评论(等价于ｆｉｌｔｅｒ函数)
#    comment_list = post.comment_set.all()
#    context = {'post':post,
#               'form':form,
#               'comment_list':comment_list}
#    return render(request,'myblog/detail.html',context=context)

# 归档
# def archives(request,year,month):
#     post_list = Post.objects.filter(created_time__year=year,created_time__month=month).order_by('-created_time')
#     return render(request,'myblog/index.html',context={'post_list':post_list})

# 分类
# def category(request,pk):
#     cate = get_object_or_404(Category,pk=pk)
#     post_list = Post.objects.filter(category=cate).order_by('-created_time')
#     return render(request,'myblog/index.html',context={'post_list':post_list})

# index类视图
class IndexView(ListView):
    model = Post
    template_name = 'myblog/index.html'
    context_object_name = 'post_list'
    # 分页功能
    paginate_by = 2

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')

        pagination_data = self.pagination_data(paginator,page,is_paginated)

        context.update(pagination_data)

        return context

    def pagination_data(self,paginator,page,is_paginated):
        if not is_paginated:
            return {}
        left = []

        right = []

        left_has_more = False

        right_has_more = False

        first = False

        last = False

        page_number = page.number

        total_pages = paginator.num_pages

        page_range = paginator.page_range

        if page_number == 1:
            right = page_range[page_number:page_number+2]

            if right[-1] < total_pages -1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True

        elif page_number == total_pages:
            left = page_range[(page_number-3) if (page_number -3) > 0 else 0 : page_number-1]

            if left[0] > 2:
                left_has_more = True

            if left[0] > 1:
                first = True

        else:
            left = page_range[(page_number -3) if (page_number -3) > 0 else 0:page_number-1]
            right = page_range[page_number:page_number+2]

            if right[-1] < total_pages -1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True


            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True

        data = {
            'left':left,
            'right':right,
            'left_has_more':left_has_more,
            'right_has_more':right_has_more,
            'first':first,
            'last':last,
        }
        return data


class CategoryView(ListView):

    model = Post
    template_name = 'myblog/index.html'
    context_object_name = 'post_list'

    '''
    ，在类视图中，从 URL 捕获的命名组参数值保存在实例的 kwargs 属性（是一个字典）里，非命名组参数值保存在实例的 args 属性（是一个列表）里。
     所以我们使了 self.kwargs.get('pk') 来获取从 URL 捕获的分类 id 值
    '''
    def get_queryset(self):
        cate = get_object_or_404(Category,pk=self.kwargs.get('pk'))
        return super(CategoryView,self).get_queryset().filter(category=cate)


class Archives(ListView):
    model = Post
    template_name = 'myblog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        year = self.kwargs.get('year')
        month =self.kwargs.get('month')
        return super(Archives,self).get_queryset().filter(created_time__year=year,created_time__month=month).order_by('-created_time')


class PostDetailView(DetailView):
    model = Post
    template_name = 'myblog/detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        # 阅读量+1
        response = super(PostDetailView,self).get(request,*args,**kwargs)
        self.object.increase_views()
        return response

    def get_object(self, queryset=None):
        # 对body渲染
        post = super(PostDetailView,self).get_object(queryset=None)
        md = markdown.Markdown(extensions=[
                                          'markdown.extensions.extra',
                                          'markdown.extensions.codehilite',
                                          TocExtension(slugify=slugify),
                                      ])

        post.body = md.convert(post.body)
        post.toc = md.toc

        return post

    def get_context_data(self, **kwargs):
        # 评论表单，post下的列表传递给模板
        context = super(PostDetailView,self).get_context_data(**kwargs)
        form = CommentForm()

        comment_list = self.object.comment_set.all()
        context.update({
            'form':form,
            'comment_list':comment_list,
        })
        return context

# 标签view
class TagView(ListView):
    model = Post
    template_name = 'myblog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        tag = get_object_or_404(Tag,pk=self.kwargs.get('pk'))
        return super(TagView,self).get_queryset().filter(tags=tag)


# def search(request):
#     q = request.GET.get('q')
#     error_msg =''
#
#     if not q:
#         error_msg = '请输入关键字'
#         return render(request,'myblog/index.html',{'error_msg':error_msg})
#     post_list = Post.objects.filter(Q(title_icontains=q) | Q(body_icontains=q))
#     return render(request,'myblog/index.html',{'error_msg':error_msg,
#                                                'post_list':post_list})

'''
def search(request):
    q = request.GET.get('q')
    error_msg = ''

    if not q:
        error_msg = "请输入关键词"
        return render(request, 'myblog/index.html', {'error_msg': error_msg})

    post_list = Post.objects.filter(Q(title__icontains=q) | Q(body__icontains=q))
    return render(request, 'myblog/index.html', {'error_msg': error_msg,
                    'post_list': post_list})
'''