from django.forms.widgets import Widget

class plusminusnumberinput(Widget):
    template_name='widgets/plusminusnumber.html'
    
    
    class Media:
        css={
            'all':('css/plusminusnumber.css',)
        }
        js=('js/plusminusnumber.js')