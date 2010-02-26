from google.appengine.ext.webapp import template
register = template.Library()

@register.filter
def inttofloat(value, arg):
    return float(value) / 1000.0;
