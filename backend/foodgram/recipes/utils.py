from django.conf import settings
from django.http import FileResponse


def shopping_txt(shop_list):
    file_name = settings.SHOPPING_CART
    lines = []
    for ing in shop_list:
        name = ing['ingredient__name']
        measurement_unit = ing['ingredient__measurement_unit']
        amount = ing['ingredient_total']
        lines.append(f'{name} ({measurement_unit}) - {amount}')
    lines.append('\nFoodGram 2024')
    content = '\n'.join(lines)
    file_path = f'/tmp/{file_name}'
    with open(file_path, 'w') as file:
        file.write(content)
    response = FileResponse(open(file_path, 'rb'),
                            as_attachment=True,
                            filename=file_name)
    return response
