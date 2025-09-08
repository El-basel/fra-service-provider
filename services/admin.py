from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Admin)
admin.site.register(Reviewer)
admin.site.register(Applicant)
admin.site.register(Service)
admin.site.register(Payment)