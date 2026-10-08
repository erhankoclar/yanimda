from django.db import migrations


def copy_to_translations(apps, schema_editor):
    """
    Eski sütunlardaki hizmet adlarını ve açıklamalarını dil satırlarına kopyalar.

    Türkçe metinler `tr`, dolu olan İngilizce karşılıklar `en` satırına yazılır.

    Args:
        apps (StateApps): Migration anındaki model kaydı.
        schema_editor (BaseDatabaseSchemaEditor): Şema düzenleyici (kullanılmaz).
    """
    ServiceType = apps.get_model('care', 'ServiceType')
    Translation = apps.get_model('care', 'ServiceTypeTranslation')
    rows = []
    for service in ServiceType.objects.all():
        rows.append(Translation(
            master_id=service.pk, language_code='tr',
            name=service.legacy_name, description=service.legacy_description,
        ))
        if service.name_en:
            rows.append(Translation(
                master_id=service.pk, language_code='en',
                name=service.name_en, description=service.description_en or service.legacy_description,
            ))
    Translation.objects.bulk_create(rows)


def copy_back(apps, schema_editor):
    """
    Geri alırken dil satırlarındaki metinleri eski sütunlara yazar.

    Args:
        apps (StateApps): Migration anındaki model kaydı.
        schema_editor (BaseDatabaseSchemaEditor): Şema düzenleyici (kullanılmaz).
    """
    ServiceType = apps.get_model('care', 'ServiceType')
    Translation = apps.get_model('care', 'ServiceTypeTranslation')
    for translation in Translation.objects.all():
        if translation.language_code == 'tr':
            fields = {'legacy_name': translation.name, 'legacy_description': translation.description}
        else:
            fields = {'name_en': translation.name, 'description_en': translation.description}
        ServiceType.objects.filter(pk=translation.master_id).update(**fields)


class Migration(migrations.Migration):
    dependencies = [
        ('care', '0007_add_service_type_translations'),
    ]

    operations = [
        migrations.RunPython(copy_to_translations, copy_back),
    ]
