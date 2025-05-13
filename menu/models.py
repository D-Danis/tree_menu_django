from django.db import models
from django.urls import reverse, NoReverseMatch

class Menu(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    menu = models.ForeignKey(Menu, related_name='items', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    url_name = models.CharField(max_length=255, blank=True)  # имя url для reverse
    url_path = models.CharField(max_length=255, blank=True)  # явный путь

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.title

    def get_url(self):
        if self.url_path:
            return self.url_path
        elif self.url_name:
            try:
                return reverse(self.url_name)
            except NoReverseMatch:
                return '#'
        else:
            return '#'