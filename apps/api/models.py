from django.db import models
from django.contrib.auth.models import User
from django.db.models import Transform
from django.db.models import CharField
# Create your models here.

class AdminProfile(models.Model):
	user=models.OneToOneField(User,on_delete=models.CASCADE)
	mobile_number=models.CharField(max_length=100)

class SpaceRemovedValue(Transform):
    lookup_name = 'nospaces'

    def as_sql(self, compiler, connection):
        lhs, params = compiler.compile(self.lhs)
        return "REPLACE(%s, ' ', '')" % lhs, params

CharField.register_lookup(SpaceRemovedValue)