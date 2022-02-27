from django.shortcuts import render, redirect
from django.urls import reverse

from recipebook.models import Ingredient, Recipe, RecipeIngredient

from recipebook.forming_list import forming_list


def home(request):
    """Главная страница. Редирект на `/recipes`"""
    response = redirect(reverse("recipe"))
    return response


def recipe(request):
    """Список рецептов с поиском по ингредиенту и названию"""

    context = {}
    search_query = request.GET.get('search', '')
    if search_query:
        recipe_search = Recipe.objects.filter(name__iexact=search_query)
        ingredient_search = Ingredient.objects.filter(name__iexact=search_query)

        if recipe_search:
            context['recipes'] = recipe_search
            recipe_name = recipe_search.first()

            ingredient_names = list(recipe_name.ingredients.all())
            ingredient_amount = RecipeIngredient.objects.filter(recipe_id=recipe_name.id).order_by('ingredient__id')

            forming_list(ingredient_names, ingredient_amount, context)

        if ingredient_search:
            ingredient_name = ingredient_search.first()
            ing_context = Recipe.objects.filter(ingredients__name__contains=ingredient_name)
            context['recipes'] = ing_context

            for elem in ing_context:
                ingredient_names = list(elem.ingredients.all())
                ingredient_amount = RecipeIngredient.objects.filter(recipe_id=elem.id).order_by('ingredient__id')

                forming_list(ingredient_names, ingredient_amount, context)

    else:
        recipes = Recipe.objects.all()[:15]
        context['recipes'] = recipes

        for elem in recipes:
            ingredient_names = list(elem.ingredients.all())
            ingredient_amount = RecipeIngredient.objects.filter(recipe_id=elem.id).order_by('ingredient__id')

            forming_list(ingredient_names, ingredient_amount, context)

    return render(request, 'recipebook/recipe.html', context)
