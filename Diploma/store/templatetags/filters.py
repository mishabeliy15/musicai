from django import template

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


register.filter('finished_orders_count', finished_orders_count)
register.filter('contains', contains)
register.filter('is_customer', is_customer)
