from django.contrib.auth import get_user_model
from django.db import models

from core.models import PublishedModel, CreatedModel
import blog.constants as const

User = get_user_model()#settings.AUTH_USER_MODEL


class Category(PublishedModel, CreatedModel):
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=const.CHAR_FIELD_LEN,
    )
    description = models.TextField(
        verbose_name='Описание',
    )
    slug = models.SlugField(
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL;'
                  ' разрешены символы латиницы, цифры, дефис и подчёркивание.',
        unique=True,
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(PublishedModel, CreatedModel):
    name = models.CharField(
        verbose_name='Название места',
        max_length=const.CHAR_FIELD_LEN,
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name




class Post(PublishedModel, CreatedModel):
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=const.CHAR_FIELD_LEN,
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем'
                  ' — можно делать отложенные публикации.',
    )
    author = models.ForeignKey(
        verbose_name='Автор публикации',
        to=User,
        on_delete=models.CASCADE,
    )
    location = models.ForeignKey(
        verbose_name='Местоположение',
        to=Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='images',
        #on_delete=models.SET_NULL,
        #null=True,
        blank=True
    )
    category = models.ForeignKey(
        verbose_name='Категория',
        to=Category,
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title

class Comment(CreatedModel):
    text = models.TextField(
        verbose_name='Текст',
    )

    author = models.ForeignKey(
        verbose_name='Автор комментария',
        to=User,
        on_delete=models.CASCADE,
    )
    post = models.ForeignKey(
        verbose_name='Комментарий публикации',
        to=Post,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Коментарии'
        ordering = ('-created_at',)

    def __str__(self):
        return str(self.id)


