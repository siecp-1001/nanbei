from datetime import datetime, timedelta
import logging
from django.contrib import admin
from django.contrib.auth.admin import (
    UserAdmin as DjangoUserAdmin
)
from django import forms
from django.utils.html import format_html
from django.db.models.functions import TruncDay
from django.db.models import Avg, Count, Min, Sum
from django.urls import path
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404, render

from django.http import HttpResponse
from django.template.loader import render_to_string

import tempfile

from . import models


class productadmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'in_stock', 'price')
    list_filter = ('active', 'in_stock', 'date_updated')
    list_editable = ('in_stock', )
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}
admin.site.register(models.product,productadmin)


class producttagadmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_filter = ('active',)
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}
   
admin.site.register(models.producttag, producttagadmin)


class productimageadmin(admin.ModelAdmin):
    list_display = ('thumbnail_tag', 'product_name')
    readonly_fields = ('thumbnail',)
    search_fields = ('product__name',)
    def thumbnail_tag(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="%s"/>' % obj.thumbnail.url
            )
        return "-"
    thumbnail_tag.short_description = "Thumbnail"
    def product_name(self, obj):
        return obj.product.name
    
admin.site.register(models.productimage, productimageadmin)

@admin.register(models.user)

class useradmin (DjangoUserAdmin):
    fieldsets=(
        (None,{"fields":("email","password")}),
        (
            "personal info",
            {"fields":("first_name","last_name")},
        ),
        (
            "permissions",
            {
                "fields":(
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                    
                )
            },
        ),
        (
            "important dates",
            {"fields":("last_login","date_joined")},
        ),
        
    )
    add_fieldsets=(
        (
            None,
            {
                "classes":("wide",),
                "fields":("email","password1","password2"),
            },
        ),
    )
    list_display=(
        "email",
        "first_name",
        "last_name",
        "is_staff"
    )
    search_fields=("email","first_name","last_name")
    ordering=("email",)
    
    
    
admin.site.register(models.adress)   
admin.site.register(models.notes) 
admin.site.register(models.basket) 
admin.site.register(models.Room) 
admin.site.register(models.Message)