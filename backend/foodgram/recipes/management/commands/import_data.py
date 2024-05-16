import csv

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        file_path = settings.BASE_DIR / '/foodgram/data/ingredients.csv'
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                Ingredient.objects.bulk_create(
                    Ingredient(name=row[0], measurement_unit=row[1])
                    for row in csv.reader(f)
                )
                self.stdout.write(
                    self.style.SUCCESS('Successfully added ingredients!')
                )
            except IntegrityError:
                self.stdout.write(
                    self.style.ERROR('Ingredients already exists!')
                )
