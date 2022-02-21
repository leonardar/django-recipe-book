from django import template

register = template.Library()


@register.filter(name='split')
def split(value, key):
    """
    Возвращает значение, преобразованное в список
    """

    return value.split(key)
