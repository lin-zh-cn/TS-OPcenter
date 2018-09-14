# -*- coding: utf-8 -*-


from rest_framework import serializers
from SaltStack import models #import Groups, Minions, Playbooks_previous, Playbooks, Jobs

class GroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Groups
        fields = "__all__"

class MinionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Minions
        fields = "__all__"

class SelectMinionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Minions
        fields = ("minion_id", "status", "jobs_count")

class PlaybooksSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True)
    class Meta:
        model = models.Playbooks
        fields = ("id","description","context","lines","status","add_time","update_time","group","group_name")

class SelectPlaybookSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Playbooks
        fields = ("description",)

class PlaybooksPreviousSerializer(serializers.ModelSerializer):
    description_name = serializers.CharField(source='release.description',read_only=True)
    class Meta:
        model = models.Playbooks_previous
        fields = ("description", "change", "update_time","description_name")

class JobsSerializer(serializers.ModelSerializer):
    description_name = serializers.CharField(source='description.description',read_only=True)
    # status_name = serializers.CharField(default="排队中",read_only=True)
    class Meta:
        model = models.Jobs
        #fields = ("status_name","description_name",)
        fields = "__all__"





