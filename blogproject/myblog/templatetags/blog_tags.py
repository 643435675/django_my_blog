from ..models import Post, Category, Tag
from django import template
from django.db.models.aggregates import Count

register = template.Library()
# 编写模板标签代码(最新的模板)
@register.simple_tag
def get_recent_posts(num=5):
    return Post.objects.all().order_by('-created_time')[:num]

# 归档模板标签（降序）
@register.simple_tag
def archives():
    return Post.objects.all().dates('created_time','month',order='DESC')

# 分类模板
@register.simple_tag
def get_categories():
    '''
    annotate 做的事情就是把全部 Category 取出来，然后去 Post 查询每一个 Category 对应的文章，
    查询完成后只需算一下每个 category id 对应有多少行记录，这样就可以统计出每个 Category 下有多少篇文章了
    :return:
    '''
    # return Category.objects.all()
    return Category.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)

# 标签云
@register.simple_tag
def get_tags():
    return Tag.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)
