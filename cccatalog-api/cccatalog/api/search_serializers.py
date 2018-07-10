from rest_framework import serializers


class ElasticsearchImageResultSerializer(serializers.Serializer):
    title = serializers.CharField(required=False)
    identifier = serializers.CharField(required=False)
    creator = serializers.CharField(required=False)
    creator_url = serializers.URLField(required=False)
    tags = serializers.ListField(required=False)
    url = serializers.URLField()
    thumbnail = serializers.URLField()
    provider = serializers.CharField(required=False)
    source = serializers.CharField(required=False)
    license = serializers.CharField()
    license_version = serializers.CharField(required=False)
    foreign_landing_url = serializers.URLField(required=False)
    meta_data = serializers.JSONField(required=False)


class ImageSearchResultSerializer(serializers.Serializer):
    result_count = serializers.IntegerField()
    page_count = serializers.IntegerField()
    results = ElasticsearchImageResultSerializer(many=True, read_only=True)
