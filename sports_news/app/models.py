from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    content = models.CharField(max_length=255, blank=True)
    link = models.URLField(unique=True)
    img_url = models.URLField(default=None)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_new = models.BooleanField(default=True)

    def __str__(self):
        return self.title
