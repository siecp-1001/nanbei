from django import forms
from django.core.mail import send_mail
from django.contrib.auth.forms import(
    UserCreationForm as Djangousercreationform
)
from django.contrib.auth.forms import UsernameField
from . import models
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.forms import inlineformset_factory
from . import widgets
import logging
from django import template

register = template.Library()
logger = logging.getLogger(__name__)
class ContactForm(forms.Form):
    name=forms.CharField(label='your name' ,max_length=100)
    message=forms.CharField(widget=forms.Textarea,max_length=600)
    def send_mail(self):
        logger.info("sending mail tO CUSTOMER SRVICE")
        message="From:{0}\n{1}".format(
            self.cleaned_data["name"],
            self.cleaned_data["message"],
            
            
        )
        send_mail(
            "site message",
            message,
            "site@booktime.domain",
            ["customerservice@booktime.domain"],
            fail_silently=False,
        )
 
class Usercreationform(Djangousercreationform):
    class Meta(Djangousercreationform.Meta):
        model=models.user
        fields=("email",)
        field_class={"email":UsernameField}
    def send_mail(self):
        logger.info(
            "sending signup email for email =%s",
            self.cleaned_data["email"],
        )
        message="welcome{}".format(self.cleaned_data["email"])
        send_mail(
            "welcome to Booktime",
            message,
            "site@booktime.domain",
            [self.cleaned_data["email"]],
            fail_silently=True,
        )        
        
        
class authenticationform(forms.Form):
    email=forms.EmailField()
    passsword= forms.CharField(
        strip=False,widget=forms.PasswordInput
    )  
    def __init__(self,request=None,*args,**kwargs):
        self.request=request
        self.user=None
        super().__init__(*args,**kwargs)
    def clean(self) :
        email=self.cleaned_data.get("email")
        password=self.cleaned_data.get("password")
        if email is not None and password:
            self.user=authenticate(
                self.request,email=email ,password=password
            )
            if self.user is None:
                raise forms.ValidationError(
                    "invalid email/password combination."
                )
            logger.info(
                "authincation is valiad for email=%s",email
            )    
        return self.cleaned_data
    def get_user(self):
        return self.user         
    






class authenticationform(AuthenticationForm):
    username = forms.EmailField(label="Email", max_length=254)

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                "This account is inactive.",
                code='inactive'
            )

BasketLineFormSet = inlineformset_factory(
    models.basket,
    models.basketline,
    fields=("quantity",),
    extra=0,
)  



@register.filter(name='add_class')
def add_class(field, css_class):
    existing_classes = field.field.widget.attrs.get('class', '')
    if existing_classes:
        css_class = existing_classes + ' ' + css_class
    return field.as_widget(attrs={"class": css_class})