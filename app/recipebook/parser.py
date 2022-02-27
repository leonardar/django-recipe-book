import psycopg2
from bs4 import BeautifulSoup
import requests
import os


def get_image(image_url) -> str:
    """
    Функция, принимающая url-адрес картинки, сохраняющая её и формирующая путь к ней в папке static
    :return: путь картинки str
    """
    dir = 'static/img/'
    path = os.path.dirname(dir)
    if not os.path.exists(path):
        os.makedirs(path)
    img_data = requests.get(image_url).content
    filename = os.path.basename(image_url)
    path = os.path.join(path, filename)
    with open(path, 'wb') as handler:
        handler.write(img_data)
    return path


def parse_url(url) -> list:
    """
    Функция, принимающая url и записывающая в список url с рецептами
    :return: list
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    items = soup.findAll('a', class_='tile is-child with-hover')
    recipes_urls = []
    for elem in items:
        link = elem['href']
        recipes_urls.append(link)
    return recipes_urls


def print_dict(d):
    """
    Функция на печать в консоль спарсенных данных
    """
    for title, inner_d in d.items():
        print(title)
        k = 'Изображение'
        print(f'\t{k}')
        print(f'\t\t{inner_d[k]}')
        k = 'Путь к изображению'
        print(f'\t{k}')
        print(f'\t\t{inner_d[k]}')
        k = 'Список ингредиентов'
        print(f'\t{k}')
        for i in inner_d[k]:
            print(f'\t\t{i}')
        print('\n')


def parse_recipes(urls: list, exception_list: list) -> dict:
    """
    Функция, которая принимает список url рецептов и заполняет словарь
    """
    dct = {}

    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('h1', class_='has-text-weight-bold').get_text(strip=True)

        if title in exception_list:
            continue
        image = soup.find('picture', class_='recipe-cover-img')
        image = image.find('img')['src']
        path = get_image(image)
        ingredients = soup.find('div', 'card-content recipe')
        final_list = ingredients.find('ul')
        final_list = final_list.findAll('li')
        lst = []
        for item in final_list:
            try:
                prod = item.find('a').get_text(strip=True)
                prod = str(prod)
                item = str(item)
                step = item.find('</a>')
                item = item[step + 4:len(item) - 5]
                item = prod + item
                item = item.capitalize()

            except:
                item = str(item)
                item = item[4:len(item) - 5]
                item = item.capitalize()
            lst.append(item)

        value_dict = {'Список ингредиентов': lst, 'Изображение': image, 'Путь к изображению': path}

        presentation_text = soup.find('div', class_='card-content').get_text(strip=True)

        value_dict['Описание блюда'] = presentation_text
        dct[title] = value_dict
    print_dict(dct)
    return dct


def db_fill(lst: list):
    """
    Функция на заполнение данными из словаря БД PostgreSQL
    """
    try:
        connection = psycopg2.connect(user="postgres",
                                      password="36499410",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="db_name")

        cursor = connection.cursor()

        for key, value in lst.items():
            dish_title = key
            dish_ingredients = ';'.join(value['Список ингредиентов'])
            print(dish_ingredients)
            dish_cooking_description = value['Описание блюда']
            dish_img_path = value['Путь к изображению']
            insert_recipe_query: str = (f"insert INTO recipebook_recipe (NAME, DESCRIPTION, img_path) VALUES ('{dish_title}','{dish_cooking_description}','{dish_img_path}') ON CONFLICT (NAME) DO UPDATE SET name=EXCLUDED.name RETURNING id")
            cursor.execute(insert_recipe_query)

            dish_id = cursor.fetchone()[0]

            dish_ingredients = value['Список ингредиентов']

            for ing in dish_ingredients:
                print(ing)
                num = ing.count(':')
                if num == 1:
                    product, quantity = ing.split(':')
                    request = f"""SELECT exists(SELECT * FROM recipebook_ingredient WHERE name = '{product}')"""
                    cursor.execute(request)
                    responce = cursor.fetchone()[0]
                    if responce is True:
                        request2 = f"""SELECT id from recipebook_ingredient where NAME = '{product}'"""
                        cursor.execute(request2)
                        product_id = cursor.fetchone()[0]
                    else:
                        insert_product_query = f"""INSERT INTO recipebook_ingredient (NAME) VALUES (\'{product}\') RETURNING id """
                        cursor.execute(insert_product_query)
                        product_id = cursor.fetchone()[0]
                        insert_recipes_query = (
                            f'INSERT INTO recipebook_recipeingredient (amount, recipe_id, ingredient_id) \n'
                            f'VALUES (\'{quantity}\',\'{dish_id}\',\'{product_id}\') RETURNING id ')
                        cursor.execute(insert_recipes_query)
                else:
                    product = ing
                    request = f"""select exists(select * from recipebook_ingredient where NAME = '{product}')"""
                    cursor.execute(request)
                    responce = cursor.fetchone()[0]
                    if responce:
                        request2 = f"""SELECT id from recipebook_ingredient where NAME = '{product}'"""
                        cursor.execute(request2)
                        product_id = cursor.fetchone()[0]
                    else:
                        insert_product_query = f"""INSERT INTO recipebook_ingredient (NAME) VALUES (\'{product}\') 
                        RETURNING id """
                        cursor.execute(insert_product_query)
                        product_id = cursor.fetchone()[0]

                        insert_recipes_query = (f'INSERT INTO recipebook_recipeingredient (amount, recipe_id, ingredient_id) \n'
                                        f'VALUES (\'{quantity}\',\'{dish_id}\',\'{product_id}\') RETURNING id ')

                        cursor.execute(insert_recipes_query)
        connection.commit()

    except Exception as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            assert isinstance(cursor, object)
            cursor.close()
            connection.close()


if __name__ == '__main__':
    exception_list = ['Говядина по-китайски: "Стир-фрай" из говядины и овощей с соусом терияки | Рецепт',
                      'Грильяж приготовится очень легко и просто в духовке',
                      'Тефтели в томатным соусе',
                      'Блины (блинчики) с курицей, морковью, шампиньонами и сыром',
                      'Суп быстрого приготовления с курицей, кокосовым молоком и консервированными грибами',
                      'Запеченные в духовке утиные или куриные желудки с картофелем фри, свежими огурцами и '
                      'йогуртовым соусом',
                      'Тушеный кролик или курица с пастой, помидорами черри и соусом песто',
                      'Куриные рулетики',
                      'В духовке запеченные куриные ножки с имбирем и зеленным луком',
                      'Карбонад с морковным слоем',
                      'Курица в остром соусе красного перца',
                      'Запеченная курица, маринованная в кефире',
                      'Пикантный салат с курицей, фасолью и сухариками из чесночного хлеба',
                      'Лазанья с курицей – итальянское блюдо',
                      'Курица, как вишня – всегда мало!',
                      'Очень вкусные и хрустящие кусочки курицы',
                      'Кисло-сладкая курица, запечённая в духовке - безумно вкусное и легко приготовляемое блюдо',
                      'Курица в панированных сухарях',
                      'Куриный салат по Грецки']

    chicken_url = 'https://worldrecipes.eu/ru/category/bliuda-iz-kuricy'
    chilen_list = parse_url(chicken_url)
    dct_chilen_list = parse_recipes(chilen_list, exception_list)
    db_fill(dct_chilen_list)
