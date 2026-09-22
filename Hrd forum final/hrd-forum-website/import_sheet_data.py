import csv
import json
import os
from datetime import date
from pathlib import Path

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrd_project.settings')
django.setup()

from django.core.management import call_command
from main_app.models import (
    Collaboration,
    Gallery,
    News,
    PopupConfig,
    Province,
    Resource,
    Stats,
    TeamMember,
    Video,
)

SHEET_PATH = Path(__file__).resolve().parent / 'data' / 'seed_data.csv'


def parse_date(value):
    return date.fromisoformat(value) if value else None


def import_sheet():
    call_command('migrate', interactive=False, verbosity=0)

    with SHEET_PATH.open(newline='', encoding='utf-8-sig') as sheet:
        rows = list(csv.DictReader(sheet))

    imported = {model: 0 for model in sorted({row['model'] for row in rows})}

    for row in rows:
        model = row['model']
        data = json.loads(row['data'])

        if model == 'stats':
            Stats.objects.update_or_create(pk=1, defaults=data)
        elif model == 'province':
            Province.objects.update_or_create(code=row['key'], defaults=data)
        elif model == 'news':
            data['published_date'] = parse_date(data.get('published_date'))
            News.objects.update_or_create(title=data['title'], defaults=data)
        elif model == 'gallery':
            Gallery.objects.update_or_create(title=data['title'], defaults=data)
        elif model == 'resource':
            Resource.objects.update_or_create(title=data['title'], defaults=data)
        elif model == 'team':
            TeamMember.objects.update_or_create(name=data['name'], defaults=data)
        elif model == 'collaboration':
            Collaboration.objects.update_or_create(name=data['name'], defaults=data)
        elif model == 'video':
            data['published_date'] = parse_date(data.get('published_date'))
            Video.objects.update_or_create(title=data['title'], defaults=data)
        elif model == 'popup':
            PopupConfig.objects.update_or_create(title=data['title'], defaults=data)
        else:
            raise ValueError(f'Unsupported model in sheet: {model}')

        imported[model] += 1

    print(f'Imported {len(rows)} sheet rows from {SHEET_PATH}')
    for model, count in imported.items():
        print(f'  {model}: {count}')


if __name__ == '__main__':
    import_sheet()
