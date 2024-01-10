"""Provides package integration into the admin panel."""

from django.contrib import admin
from .models import UserLog

admin.site.register(UserLog)
