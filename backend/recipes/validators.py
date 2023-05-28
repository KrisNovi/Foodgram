from django.core.exceptions import ValidationError


def validate_amount(value):
    if value <= 0:
        raise ValidationError('Количество должно быть больше 0')
