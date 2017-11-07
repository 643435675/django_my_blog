from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
import markdown
# Create your models here.

# 装饰器用于兼容python2
# @python_2_unicode_compatible
from django.utils.html import strip_tags


class Category(models.Model):
    '''
    Django 要求模型必须继承 models.Model 类。
    Category 只需要一个简单的分类名 name 就可以了。
    CharField 指定了分类名 name 的数据类型，CharField 是字符型，
    CharField 的 max_length 参数指定其最大长度，超过这个长度的分类名就不能被存入数据库。
    当然 Django 还为我们提供了多种其它的数据类型，如日期时间类型 DateTimeField、整数类型 IntegerField 等等。
    Django 内置的全部类型可查看文档：
    https://docs.djangoproject.com/en/1.10/ref/models/fields/#field-types
    '''
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Tag(models.Model):
    """
       标签 Tag 也比较简单，和 Category 一样。
       再次强调一定要继承 models.Model 类！
    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Post(models.Model):
    '''
    文章涉及的字段多
    '''

    #标题
    title = models.CharField(max_length=70)

    body = models.TextField()

    created_time = models.DateTimeField()
    
    modified_time = models.DateTimeField()
    # 摘要
    excerpt = models.CharField(max_length=200,blank=True)

    category = models.ForeignKey(Category)

    tags = models.ManyToManyField(Tag,blank=True)

    author = models.ForeignKey(User)

    # 记录阅读量
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('myblog:detail',kwargs={'pk':self.pk})

    def increase_views(self):
        self.views +=1
        self.save(update_fields=['views'])


    def save(self, *args, **kwargs):
        # 如果没有填写摘要
        if not self.excerpt:
            # 首先实例化一个 Markdown 类，用于渲染 body 的文本
            md = markdown.Markdown(extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
            ])
            # 先将 Markdown 文本渲染成 HTML 文本
            # strip_tags 去掉 HTML 文本的全部 HTML 标签
            # 从文本摘取前 54 个字符赋给 excerpt
            self.excerpt = strip_tags(md.convert(self.body))[:54]

            # 调用父类的 save 方法将数据保存到数据库中

        super(Post, self).save(*args, **kwargs)

    # 这用于按照时间排序
    class Meta:
        ordering = ['-created_time']


