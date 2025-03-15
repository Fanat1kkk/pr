from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from ckeditor.fields import RichTextField

class BlogPost(models.Model):
    title = models.CharField(max_length=300, verbose_name="Заголовок")
    slug = models.SlugField(unique=True, blank=True, null=True)
    image = models.ImageField(upload_to="blog_images/", verbose_name="Изображение", blank=True, null=True)
    content = RichTextField(verbose_name="Содержание")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    meta_description = models.CharField(max_length=160, verbose_name="SEO Description", blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Блог"
        verbose_name_plural = "Блог"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title
