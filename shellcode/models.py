from django.db import models

# Create your models here.


class Shellcode(models.Model):
    id = models.AutoField(primary_key=True)
    hash_md5 = models.CharField(max_length=200)
    shellcode = models.TextField()
    pub_date = models.DateTimeField(auto_now=True)
    number = models.IntegerField()
    packaging = models.CharField(max_length=200)
    filename = models.FileField(max_length=200)

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.shellcode
