from django.db import models


class PublishedModel(models.Model):
    is_published = models.BooleanField(
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.',
        default=True,
    )

    class Meta:
        abstract = True


class CreatedModel(models.Model):
    created_at = models.DateTimeField(
        verbose_name='Добавлено',
        auto_now_add=True,
    )

    class Meta:
        abstract = True
