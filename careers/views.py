from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Post
from .serializers import PostSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    @action(detail=False, methods=['get'])
    def get(self, request):
        queryset = Post.objects.all()
        serializer = PostSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def retrieve(self, request, pk=None):
        post = self.get_object()
        serializer = PostSerializer(post)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['patch'])
    def patch(self, request, pk=None):
        post = self.get_object()
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['delete'])
    def delete(self, request, pk=None):
        post = self.get_object()
        post.delete()
        return Response({'message': 'Post deleted successfully'},status=204)