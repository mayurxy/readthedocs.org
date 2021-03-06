"""Defines serializers for each of our models."""

from __future__ import absolute_import
from builtins import object

from rest_framework import serializers

from readthedocs.builds.models import Build, BuildCommandResult, Version
from readthedocs.projects.models import Project, Domain
from readthedocs.oauth.models import RemoteOrganization, RemoteRepository


class ProjectSerializer(serializers.ModelSerializer):
    canonical_url = serializers.ReadOnlyField(source='get_docs_url')

    class Meta(object):
        model = Project
        fields = (
            'id',
            'name', 'slug', 'description', 'language',
            'repo', 'repo_type',
            'default_version', 'default_branch',
            'documentation_type',
            'users',
            'canonical_url',
        )


class ProjectAdminSerializer(ProjectSerializer):

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + (
            'enable_epub_build',
            'enable_pdf_build',
            'conf_py_file',
            'analytics_code',
            'cdn_enabled',
            'container_image',
            'container_mem_limit',
            'container_time_limit',
            'install_project',
            'use_system_packages',
            'suffix',
            'skip',
            'requirements_file',
            'python_interpreter',
        )


class VersionSerializer(serializers.ModelSerializer):
    project = ProjectSerializer()
    downloads = serializers.DictField(source='get_downloads', read_only=True)

    class Meta(object):
        model = Version
        fields = (
            'id',
            'project', 'slug',
            'identifier', 'verbose_name',
            'active', 'built',
            'downloads',
        )


class VersionAdminSerializer(VersionSerializer):

    """Version serializer that returns admin project data"""

    project = ProjectAdminSerializer()


class BuildCommandSerializer(serializers.ModelSerializer):

    run_time = serializers.ReadOnlyField()

    class Meta(object):
        model = BuildCommandResult
        exclude = ('')


class BuildSerializer(serializers.ModelSerializer):

    """Build serializer for user display, doesn't display internal fields"""

    commands = BuildCommandSerializer(many=True, read_only=True)
    state_display = serializers.ReadOnlyField(source='get_state_display')

    class Meta(object):
        model = Build
        exclude = ('builder',)


class BuildAdminSerializer(BuildSerializer):

    """Build serializer for display to admin users and build instances"""

    class Meta(BuildSerializer.Meta):
        exclude = ()


class SearchIndexSerializer(serializers.Serializer):
    q = serializers.CharField(max_length=500)
    project = serializers.CharField(max_length=500, required=False)
    version = serializers.CharField(max_length=500, required=False)
    page = serializers.CharField(max_length=500, required=False)


class DomainSerializer(serializers.ModelSerializer):
    project = ProjectSerializer()

    class Meta(object):
        model = Domain
        fields = (
            'id',
            'project',
            'domain',
            'canonical',
            'machine',
            'cname',
        )


class RemoteOrganizationSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = RemoteOrganization
        exclude = ('json', 'email', 'users')


class RemoteRepositorySerializer(serializers.ModelSerializer):

    """Remote service repository serializer"""

    organization = RemoteOrganizationSerializer()
    matches = serializers.SerializerMethodField()

    class Meta(object):
        model = RemoteRepository
        exclude = ('json', 'users')

    def get_matches(self, obj):
        request = self.context['request']
        if request.user is not None and request.user.is_authenticated():
            return obj.matches(request.user)
