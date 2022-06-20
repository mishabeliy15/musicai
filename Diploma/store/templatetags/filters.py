from django import template
import re

register = template.Library()

def contains(collection, item):
    return collection.contains(item)


def is_customer(user):
    try:
        client = user.customer
        return True
    except:
        return False


def finished_orders_count(composer):
    try:
        return composer.composerorder_set.filter(finish=True).count()
    except:
        return 0

def remove_lang_code(url):
    url = re.sub(r'/?(uk|en)/?', "", url)

    if url == '' or url == '/':
        return ''

    return '/' + url


def replace(value, arg):
    if len(arg.split('|')) != 2:
        return value

    what, to = arg.split('|')
    return value.replace(what, to)

register.filter('finished_orders_count', finished_orders_count)
register.filter('contains', contains)
register.filter('is_customer', is_customer)
register.filter('remove_lang_code', remove_lang_code)
register.filter('replace', replace)
