from os import path
import os
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from main.forms import ContactForm, TourProgramForm, authenticationform
from django.contrib.auth.views import LoginView as DjangoLoginView
from webpush import send_user_notification
from django.conf import settings
from django.contrib.auth.models import User
import logging
import os
from django.conf import settings
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from main.forms import ContactForm, TourProgramForm
from .models import Contact,TourProgram, ProgramOption
from main import forms, models
from .models import Contact, TourProgram, basketline, product, Room, Message

logger = logging.getLogger(__name__)

@method_decorator(sensitive_post_parameters(), name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class CustomLoginView(DjangoLoginView):
    authentication_form = authenticationform
    template_name = "login.html"
    redirect_authenticated_user = True
    next_page = reverse_lazy("main:home")

    def form_valid(self, form):
        """Log the user in and display a message."""
        login(self.request, form.get_user())   # THIS LINE SHOULD BE HERE
        messages.success(self.request, "You have successfully logged in.")
        logger.info(f"Login successful: {form.get_user().email}")
        return super().form_valid(form)

    def form_invalid(self, form):
        """Handle login errors with a message."""
        messages.error(self.request, "Invalid credentials. Please try again.")
        logger.warning(f"Login failed: {form.data}")
        return super().form_invalid(form)
# Home and About Us Views (public)
def home(request):
    return render(request, "pages/home.html", {})

def about_us(request):
    return render(request, "pages/about_us.html", {})

# Contact Us form view (public)
class Contactusview(FormView):
    template_name = "pages/contact_form.html"
    form_class = forms.ContactForm
    success_url = "/"

    def form_valid(self, form):
        form.send_mail()
        return super().form_valid(form)

# Product List View (public)
class productlistview(ListView):
    template_name = "pages/product_list.html"
    model = models.product
    paginate_by = 7
    context_object_name = "products"

    def get_queryset(self):
        return product.objects.filter(active=True)[:7]

# Chat Room List View (requires login)


class roomlistview(LoginRequiredMixin, ListView):
    template_name = "chat.html"
    model = models.Room
    paginate_by = 10
    context_object_name = "rooms"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vapid_key'] = settings.WEBPUSH_SETTINGS["VAPID_PUBLIC_KEY"]
        return context


# Signup view (public)
class signupview(FormView):
    template_name = "signup.html"
    form_class = forms.Usercreationform

    def get_success_url(self):
        redirect_to = self.request.GET.get("next", "/")
        return redirect_to

    def form_valid(self, form):
        response = super().form_valid(form)
        form.save()
        email = form.cleaned_data.get("email")
        raw_password = form.cleaned_data.get("password1")
        logger.info("New signup for email=%s through signupview", email)
        user = authenticate(email=email, password=raw_password)
        login(self.request, user)
        form.send_mail()
        messages.info(self.request, "You signed up successfully")
        return response

# Address Views (all require login)
class adresslistview(LoginRequiredMixin, ListView):
    model = models.adress

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

class adresscreateview(LoginRequiredMixin, CreateView):
    model = models.adress
    fields = [
        "name",
        "fromv",
        "to",
        "driver",
        "city",
        "country",
    ]
    success_url = reverse_lazy("main:adress_list")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        return super().form_valid(form)

class adressupdateview(LoginRequiredMixin, UpdateView):
    model = models.adress
    fields = [
        "name",
        "fromv",
        "to",
        "driver",
        "city",
        "country",
    ]
    success_url = reverse_lazy("main:adress_list")

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

class adressdeleteview(LoginRequiredMixin, DeleteView):
    model = models.adress
    success_url = reverse_lazy("main:adress_list")

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

# Chat Views (require login)
@login_required
def room(request, room):
    username = request.GET.get('username', request.user.email)
    room_details = get_object_or_404(Room, name=room)
    return render(request, 'room.html', {
        'username': username,
        'room': room,
        'room_details': room_details
    })


@login_required
def checkview(request):
    room = request.POST['room_name']
    username = request.POST.get('username', request.user.email)

    if Room.objects.filter(name=room).exists():
        return redirect(f'/{room}/?username={username}')
    else:
        new_room = Room.objects.create(name=room)
        return redirect(f'/{room}/?username={username}')

@login_required
def send(request):
    message = request.POST['message']
    room_id = request.POST['room_id']
    username = request.POST.get('username', request.user.email)

    # Save message
    new_message = Message.objects.create(value=message, user=username, room=room_id)
    new_message.save()

    # Notify all users in the room (you can customize this to only send to others)
    room_obj = Room.objects.get(pk=room_id)
    users_in_room = User.objects.exclude(pk=request.user.pk)  # all except current user

    payload = {
        "head": "New Chat Message",
        "body": f"{username}: {message}",
        "url": f"/{room_obj.name}/"
    }

    for user in users_in_room:
        try:
            send_user_notification(user=user, payload=payload, ttl=1000)
        except Exception as e:
            print("Notification error:", e)

    return HttpResponse('Message sent successfully')

@login_required
def getMessages(request, room):
    room_details = Room.objects.get(name=room)
    messages = Message.objects.filter(room=room_details.id)
    return JsonResponse({"messages": list(messages.values())})

# Basket Views (require login)
@login_required
def add_to_basket(request):
    product = get_object_or_404(models.product, pk=request.GET.get("product_id"))
    basket = getattr(request, 'basket', None)

    if not basket:
        basket = models.basket.objects.create(user=request.user)
        request.session["basket_id"] = basket.id

    basketline, created = models.basketline.objects.get_or_create(
        basket=basket, product=product
    )
    if not created:
        basketline.quantity += 1
        basketline.save()

    return HttpResponseRedirect(reverse("main:product", args=(product.slug,)))

@login_required
def manage_basket(request):
    if not hasattr(request, 'basket') or not request.basket:
        return render(request, "basket.html", {"formset": None})

    if request.method == "POST":
        formset = forms.BasketLineFormSet(request.POST, instance=request.basket)
        if formset.is_valid():
            formset.save()
    else:
        formset = forms.BasketLineFormSet(instance=request.basket)

    if request.basket.is_empty():
        return render(request, "basket.html", {"formset": None})

    return render(request, "basket.html", {"formset": formset})

# Notes Views (require login)
class notelistview(LoginRequiredMixin, ListView):
    model = models.notes

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

class notecreateview(LoginRequiredMixin, CreateView):
    model = models.notes
    fields = [
        "NOTE",
        "date",
    ]
    success_url = reverse_lazy("main:notes_list")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        return super().form_valid(form)

class noteupdateview(LoginRequiredMixin, UpdateView):
    model = models.notes
    fields = [
        "NOTE",
        "date",
    ]
    success_url = reverse_lazy("main:notes_list")

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

class notedeleteview(LoginRequiredMixin, DeleteView):
    model = models.notes
    success_url = reverse_lazy("main:notes_list")

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)





def add_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_contacts')
    else:
        form = ContactForm()
    return render(request, 'add_contact.html', {'form': form})


# View to list all contacts
def list_contacts(request):
    contacts = Contact.objects.all()
    return render(request, 'list_contacts.html', {'contacts': contacts})


# View to generate a PDF of contacts
def print_contacts_pdf(request):
    contacts = Contact.objects.all()
    template = get_template('contacts/contacts_pdf.html')

    # Get the full path to the font file
    font_path = os.path.join(settings.BASE_DIR, 'static', 'Rubik-VariableFont_wght.ttf')

    # Render the template with the context
    html = template.render({'contacts': contacts, 'font_path': font_path})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="contacts.pdf"'

    # Create the PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        # Handle PDF generation errors
        return HttpResponse('Failed to generate PDF. Please check your template and font file path.')

    return response


# View to display contacts for selection
def select_contacts(request):
    contacts = Contact.objects.all()
    return render(request, 'contacts/select_contacts.html', {'contacts': contacts})





def add_tour_program(request):
    if request.method == 'POST':
        form = TourProgramForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('main:list_tour_programs')  # Redirect to list after saving
    else:
        form = TourProgramForm()

    return render(request, 'add_tour.html', {'form': form})


# View to List Saved Tour Programs
def list_tour_programs(request):
    programs = TourProgram.objects.all()
    return render(request, 'list_tour.html', {'programs': programs})



def my_view(request):
    menu_items = [
        ('Home', '/'),
        ('About Us', '/about-us/'),
        ('Contact Us', '/contact-us/'),
        ('Products', '/products/'),
        ('Signup', '/signup/'),
        ('Login', '/login/'),
        ('Address', '/address/'),
        ('Your Basket', '/basket/'),
        ('Chat', '/chat/'),
        ('Notes', '/note/'),
        ('Contacts', '/contacts/'),  # List contacts
        ('Add Contact', '/add-contact/'),
        ('Print Contacts PDF', '/print-contacts-pdf/'),
        ('Select Contacts', '/select-contacts/'),
        ('Tour Programs', '/tour-programs/'),  # List tour programs
        ('Add Tour Program', '/add-tour/'),
    ]
    return render(request, 'template.html', {'menu_items': menu_items})

