from django.shortcuts import render, redirect
from django.urls import reverse

from recipebook.models import Ingredient, Recipe


def home(request):
    """Главная страница. Редирект на `/recipes`"""
    response = redirect(reverse("recipe"))
    return response


def recipe(request):
    """Список рецептов с поиском по ингредиенту и названию"""

    context = {}
    search_query = request.GET.get('search', '')
    if search_query:
        recipe_search = Recipe.objects.filter(name=search_query)
        ingredient_search = Ingredient.objects.filter(name=search_query)
        # проверка на ввод рецепта
        if recipe_search:
            context['recipes'] = recipe_search

        # проверка на ввод ингредиента
        if ingredient_search:
            ingredient_name = ingredient_search.first()
            ing_context = Recipe.objects.filter(ingredients=ingredient_name)
            context['recipes'] = ing_context
    else:
        recipes = Recipe.objects.all()[:20] # ограничение на кол-во вывода (временная заглушка без добавления пагинации)
        context['recipes'] = recipes

    return render(request, 'recipebook/recipe.html', context)
