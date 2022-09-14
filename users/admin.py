"""Provides package integration into the admin panel."""

from django.contrib import admin
from .models import MyUser

admin.site.register(MyUser)
