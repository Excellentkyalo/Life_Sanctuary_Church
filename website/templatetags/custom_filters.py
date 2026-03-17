# website/templatetags/custom_filters.py
from django import template
import re

register = template.Library()

@register.filter
def youtube_embed(url):
    """Convert YouTube URL to embed URL"""
    if not url:
        return ''
    
    # Handle different YouTube URL formats
    if 'youtu.be/' in url:
        video_id = url.split('youtu.be/')[-1].split('?')[0].split('&')[0]
        return f'https://www.youtube.com/embed/{video_id}'
    elif 'youtube.com/watch?v=' in url:
        video_id = url.split('v=')[-1].split('&')[0]
        return f'https://www.youtube.com/embed/{video_id}'
    elif 'youtube.com/embed/' in url:
        return url
    else:
        return url

@register.filter
def truncatewords_html(value, arg):
    """Truncate HTML content after certain number of words"""
    try:
        arg = int(arg)
    except ValueError:
        return value
    
    from django.utils.html import strip_tags
    text = strip_tags(value)
    words = text.split()
    
    if len(words) > arg:
        return ' '.join(words[:arg]) + '...'
    
    return value