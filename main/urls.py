from django.urls import path
from .  import views
from django.views.generic import TemplateView
from main import views,models

from django.views.generic.detail import DetailView
from django.contrib.auth import views as auth_views
from main import forms
app_name='main'
urlpatterns =  [ 
    path("add_to_basket/",views.add_to_basket,name="add_to_basket")  , 
             
    path( "products/", views.productlistview.as_view(), name="products" ),
    path('basket/', views.manage_basket, name="basket"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
 

    path("note/",views.notelistview.as_view(),name="notes_list"),
    path("note/create/",views.notecreateview.as_view(),name='note_create'),
    path("address/<int:pk>/",views.noteupdateview.as_view(),name="note_update"),
    path("address/<int:pk>/delete/",views.notedeleteview.as_view(),name="note_delete",),
    path("address/",views.adresslistview.as_view(),name="adress_list"),
    path("address/create/",views.adresscreateview.as_view(),name='address_create'),
    path("address/<int:pk>/",views.adressupdateview.as_view(),name="address_update"),
    path("address/<int:pk>/delete/",views.adressdeleteview.as_view(),name="address_delete",),             
    path("login/",auth_views.LoginView.as_view(template_name="login.html",form_class=forms.authenticationform,),name="login",),
    path("signup/", views.signupview.as_view(), name="signup"),
    path("products/<slug:tag>/", views.productlistview.as_view(),name="products",),
    path("product/<slug:slug>/", DetailView.as_view(model= models.product),name="product",),
    path("contact-us/",views.Contactusview.as_view()),
    path("about-us/",TemplateView.as_view(template_name="pages/about_us.html"),name="about_us",),
    path("",TemplateView.as_view(template_name="pages/home.html"),name="home",),
     path( "products/", views.roomlistview.as_view(), name="products" ),
    path('chat/', views.roomlistview.as_view(), name='home'),
    path('<str:room>/', views.room, name='room'),
    path('chat/checkview', views.checkview, name='checkview'),
    path('send', views.send, name='send'),
    path('getMessages/<str:room>/', views.getMessages, name='getMessages'),
    
]
   
     


