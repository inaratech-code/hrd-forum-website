from django.db import migrations, models


def clear_seeded_metrics(apps, schema_editor):
    Stats = apps.get_model('main_app', 'Stats')
    UniqueVisitor = apps.get_model('main_app', 'UniqueVisitor')
    Stats.objects.filter(
        monitored_defenders=1200,
        resolved_cases=150,
    ).update(
        monitored_defenders=0,
        resolved_cases=0,
        total_visitors=UniqueVisitor.objects.count(),
    )


class Migration(migrations.Migration):
    dependencies = [('main_app', '0018_organizationalupdate')]

    operations = [
        migrations.AlterField(
            model_name='stats',
            name='monitored_defenders',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='stats',
            name='resolved_cases',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.RunPython(clear_seeded_metrics, migrations.RunPython.noop),
    ]
