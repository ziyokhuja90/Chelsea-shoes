from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''

    
def _phone_digits(value):
    return ''.join(filter(str.isdigit, str(value or '')))


@register.filter
def format_phone(value):
    digits = _phone_digits(value)
    if not digits:
        return ''
    phone_str = digits[-9:].zfill(9)
    return f"({phone_str[:2]}) {phone_str[2:5]}-{phone_str[5:7]}-{phone_str[7:]}"


@register.simple_tag
def inc_counter(counter):
    try:
        return counter + 1
    except:
        return 1