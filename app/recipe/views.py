
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from recipe.serializers import IngredientSerializer
from recipe.serializers import *
from core.models import Recipe, Tag, Ingredient
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

@extend_schema_view(
    list = extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma separated list of IDs to filter',
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separated list of ingredient IDs to filter',
            )
        ]
    )
)

class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Recipe.objects.all()
    
    def _params_to_ints(self, qs):
        return [int(str_id for str_id in qs.split(','))]
    
    def get_queryset(self):
        tags = self.request.query_params.get('ingredients')
        Ingredients = self.request.query_params.get('ingredient')
        queryset= self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if Ingredients:
            ingredient_ids = self._params_to_ints(Ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)
        return queryset.filter(user=self.request.user).order_by('-id').distinct()
        
    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeSerializer
        if self.action == 'upload_image':
            return RecipeImageSerializer
        return self.get_serializer_class
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk =None):
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status
                        .HTTP_400_BAD_REQUEST)


class BaseRecipeViewSet(mixins.DestroyModelMixin,
                mixins.UpdateModelMixin,
                mixins.ListModelMixin, 
                viewsets.GenericViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-name')


class TagViewSet(BaseRecipeViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()

    
class IngredientViewSet(BaseRecipeViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    
   