from django.db import models


class Ingredient(models.Model):
    """
    Модель ингредиента:
    name - название ингредиента
    """

    name = models.CharField(
        max_length=400,
        verbose_name='Название ингредиента',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    """
    Модель рецепта:
    name - название рецепта,
    description - описание рецепта,
    ingredients - ингредиенты рецепта
    """

    name = models.TextField(
        max_length=400,
        verbose_name='Название рецепта',
        unique=True,
    )
    description = models.TextField(
        max_length=1000,
        verbose_name='Описание рецепта',
        blank=True,
    )

    img_path = models.CharField(
        max_length=200,
        verbose_name='Путь к картинке',
        blank=True
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredient(models.Model):
    """
    Модель, формирующая связи рецептов с ингредиентами:
    recipe - рецепт,
    ingredient - ингредиент,
    amount - количество ингредиента
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )

    amount = models.CharField(
        max_length=128,
        verbose_name='Количество ингредиента'
    )
