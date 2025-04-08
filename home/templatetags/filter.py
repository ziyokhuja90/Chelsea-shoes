from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''

    
@register.filter
def format_phone(value):
    phone_str = str(value).zfill(9)
    return f"({phone_str[:2]}) {phone_str[2:5]}-{phone_str[5:7]}-{phone_str[7:]}"