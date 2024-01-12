from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id','username', 'created_datetime', 'updated_datetime', 'title', 'content']
        read_only_fields = ['id', 'created_datetime', 'updated_datetime']

    def update(self, instance, validated_data):
        # Override update method to prevent updating 'username'
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance
