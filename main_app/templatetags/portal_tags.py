from django import template

register = template.Library()

@register.filter(name='attribute')
def get_attribute(value, arg):
    """Dynamically fetch an attribute or callable from an object."""
    if value is None or not arg:
        return ''
    
    if hasattr(value, str(arg)):
        attr = getattr(value, str(arg))
        if callable(attr):
            try:
                return attr()
            except Exception:
                return str(attr)
        return attr
    
    if isinstance(value, dict):
        return value.get(arg, '')
        
    return ''
