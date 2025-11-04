from django import template
register = template.Library()

@register.filter
def dict_get(d, key):
    """Return d.get(str(key)) or d.get(key) or None. Safe lookup for JSONField dicts."""
    try:
        if d is None:
            return None
        # prefer string key (we store days as strings)
        k = str(key)
        if isinstance(d, dict):
            return d.get(key) if key in d else d.get(str(key))
    except Exception:
        return None
    return None

@register.filter
def key(d, k):
    return d.get(k)