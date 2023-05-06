from django.db import models

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USERNAME_FIELD = 'email'

    USER = 'user'
    ADMIN = 'admin'

    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name'
    )

    ROLE_CHOICES = [
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
    ]
    username = models.SlugField(unique=True, verbose_name='Логин')
    email = models.EmailField(
        unique=True,
        verbose_name='Адрес электронной почты'
    )
    role = models.CharField(
        max_length=255,
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Роль'
    )
    confirmation_code = models.CharField(
        blank=True,
        max_length=255,
        null=True
    )
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_user(self):
        return self.role == self.USER
