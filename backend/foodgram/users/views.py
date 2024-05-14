from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.pagination import RecipePagination
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .models import Subscription, User
from .serializers import (AvatarSerializer, MyUserSerializer,
                          SubscribSerializer, SubscriptionSerializer)


class MyUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = MyUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = RecipePagination

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        """Кастомное получение профиля пользователя."""
        user = self.request.user
        serializer = MyUserSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(
        methods=['GET', 'PUT'],
        permission_classes=[IsAuthenticated],
        detail=False,
        url_name='avatar',
        url_path='me/avatar'
    )
    def change_avatar(self, request):
        """Функция для добавления и смены аватара"""
        avatar = self.request.user
        serializer = AvatarSerializer(avatar, data=request.data)
        if (serializer.is_valid() and request.method == 'PUT'
           and 'avatar' in request.data):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @change_avatar.mapping.delete
    def delete_avatar(self, request):
        """Функция для удаления аватара"""
        avatar = self.request.user
        serializer = AvatarSerializer(avatar, data=request.data)
        if serializer.is_valid():
            request.user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True, methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,),
        url_path='subscribe', url_name='subscribe'
    )
    def subscribe(self, request, id):
        """Метод для управления подписками """
        user = request.user
        author = get_object_or_404(User, id=id)
        change_subscription_status = Subscription.objects.filter(
            user=user.id, author=author.id
        )
        serializer = SubscribSerializer(
            data={'user': user.id, 'author': author.id},
            context={'request': request}
        )
        if request.method == 'POST':
            if user == author:
                return Response('Вы пытаетесь подписаться на себя!!',
                                status=status.HTTP_400_BAD_REQUEST)
            if change_subscription_status.exists():
                return Response(f'Вы уже подписаны на {author}',
                                status=status.HTTP_400_BAD_REQUEST)
            serializer.is_valid()
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        if change_subscription_status.exists():
            change_subscription_status.delete()
            return Response(f'Вы отписались от {author}',
                            status=status.HTTP_204_NO_CONTENT)
        return Response(f'Вы не подписаны на {author}',
                        status=status.HTTP_400_BAD_REQUEST)


class SubscriptionViewSet(ListAPIView):
    serializer_class = SubscriptionSerializer
    pagination_class = RecipePagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return user.follower.all()
