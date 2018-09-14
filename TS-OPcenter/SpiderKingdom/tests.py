from django.test import TestCase
import django
import os,sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.chdir(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TS.settings")
django.setup()
# Create your tests here.
from SpiderKingdom import models

l = [2,3]
ret = models.Node.objects.in_bulk(l)
for k,y in ret.items():
    print(y.node)
