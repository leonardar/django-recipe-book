# Generated by Django 3.2.12 on 2022-02-21 23:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipebook', '0002_auto_20220221_2347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]