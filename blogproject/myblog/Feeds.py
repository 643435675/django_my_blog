from django.contrib.syndication.views import Feed

from .models import Post

#订阅
class AllPostsRssFeed(Feed):

     #显示在聚合阅读器上的标题
     title = "Django 博客教程"

     #通过聚合器跳转到的网址
     link = "/"

     description = "Django 演示描述信息"

     #需要显示的条目
     def items(self):
         return Post.objects.all()

     #聚合器中显示的条目标题
     def item_title(self, item):
         return '[%s] %s ' % (item.category,item.title)

     #聚合器中显示的内容描述
     def item_description(self, item):
         return item.body