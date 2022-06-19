import django
from django.db import models

# Create your models here.
from django.db import models
 # 导入内建的user模型
from django.contrib.auth.models import User
# timezone 用于处理时间相关事务
from django.utils import timezone
from taggit.managers import TaggableManager
from PIL import Image

class ArticleColumn(models.Model):
    title = models.CharField(max_length=100, blank=True)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class ArticlePost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000)
    body = models.TextField()
    created = models.DateTimeField(default=django.utils.timezone.now)
    tags = TaggableManager(blank=True)
    avatar = models.ImageField(upload_to='article/%Y%m%d/', blank=True)
    total_views = models.PositiveIntegerField(default=0)
    updated = models.DateTimeField(auto_now=True)
    column = models.ForeignKey(
        ArticleColumn,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='article'
    )
    objects = models.Manager()

    def save(self, *args, **kwargs):
        article = super(ArticlePost, self).save( *args, **kwargs)

        if self.avatar and not kwargs.get('update_fields'):
            image = Image.open(self.avatar)
            (x, y) = image.size
            new_x = 400
            new_y = int(new_x * (y / x))
            resized_image = image.resize((new_x, new_y), Image.ANTIALIAS)
            resized_image.save(self.avatar.path)
        return article


    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.title