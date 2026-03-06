from django.db import models


class Video(models.Model):
    CATEGORY_CHOICES = [
        ('Drama', 'Drama'),
        ('Comedy', 'Comedy'),
        ('Romance', 'Romance'),
        ('Action', 'Action'),
        ('Thriller', 'Thriller'),
        ('Horror', 'Horror'),
        ('Documentary', 'Documentary'),
        ('Animation', 'Animation'),
    ]

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    video_file = models.FileField(upload_to='videos/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'

    def __str__(self):
        return self.title
