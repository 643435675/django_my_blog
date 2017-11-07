from django.shortcuts import render
from django.shortcuts import get_object_or_404,redirect
from .forms import CommentForm
from .models import Comment
from myblog.models import Post
from .models import Comment
from .forms import CommentForm

# Create your views here.

def post_comment(request,post_pk):
    post = get_object_or_404(Post,pk=post_pk)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        #是否符合格式要求
        if form.is_valid():
            # 生成实例，并不保存
            comment = form.save(commit=False)

            # 评论和被评论文章相关联起来
            comment.post = post

            comment.save()

            # 重定向到post详情页， 函数接收一个模型的实例时，它会调用这个模型实例的 get_absolute_url 方法，
            # 然后重定向到 get_absolute_url 方法返回的 URL。
            return redirect(post)

        else:
            comment_list = post.comment_set.all()
            context = {'post':post,
                       'form':form,
                       'comment_list':comment_list}
            return render(request,'myblog/detail.html',context=context)
        # 不是post请求，重定向到文章详情页
    return redirect(post)