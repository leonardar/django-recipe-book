def forming_list(ingredient_names, ingredient_amount, context):
    ingredient_names_amount = []

    for elem in range(len(ingredient_names)):
        ingredient_names_amount.append(f'{ingredient_names[elem]}: {ingredient_amount[elem].amount}')

    context.update({'ingredient_names_amount': ingredient_names_amount})
