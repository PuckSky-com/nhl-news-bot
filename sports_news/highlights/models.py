from django.db import models

class Video(models.Model):
    vid_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    img_url = models.URLField(default=None)
    embed_url = models.URLField(unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_new = models.BooleanField(default=True)

    def __str__(self):
        return self.title
