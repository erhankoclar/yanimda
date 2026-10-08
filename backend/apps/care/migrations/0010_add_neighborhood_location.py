import django.db.models.deletion
from django.db import migrations, models


def move_city_district_into_address(apps, schema_editor):
    """
    Eski serbest metin il ve ilçeyi, kaybolmasın diye adresin sonuna ekler.

    Mahalle bu kayıtlar için bilinmediğinden `neighborhood` boş kalır.

    Args:
        apps (StateApps): Migration anındaki model kaydı.
        schema_editor (BaseDatabaseSchemaEditor): Şema düzenleyici (kullanılmaz).
    """
    CareRequest = apps.get_model('care', 'CareRequest')
    for care_request in CareRequest.objects.exclude(city='', district=''):
        place = ' / '.join(part for part in (care_request.district, care_request.city) if part)
        care_request.address = f'{care_request.address}, {place}'
        care_request.save(update_fields=['address'])


def restore_city_district(apps, schema_editor):
    """
    Geri alırken ili İstanbul, ilçeyi mahallenin ilçesi olarak yazar; mahalle yoksa boş bırakır.

    Args:
        apps (StateApps): Migration anındaki model kaydı.
        schema_editor (BaseDatabaseSchemaEditor): Şema düzenleyici (kullanılmaz).
    """
    CareRequest = apps.get_model('care', 'CareRequest')
    for care_request in CareRequest.objects.select_related('neighborhood__district'):
        care_request.city = 'İstanbul'
        care_request.district = care_request.neighborhood.district.name if care_request.neighborhood else ''
        care_request.save(update_fields=['city', 'district'])


class Migration(migrations.Migration):
    """Başvuru ve hızlı taleplere mahalle konumu ekler; serbest metin il/ilçeyi kaldırır."""

    dependencies = [
        ('care', '0009_remove_service_type_legacy_fields'),
        ('geo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='carerequest',
            name='neighborhood',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='care_requests', to='geo.neighborhood', verbose_name='neighborhood'),
        ),
        migrations.AddField(
            model_name='serviceinquiry',
            name='neighborhood',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='inquiries', to='geo.neighborhood', verbose_name='neighborhood'),
        ),
        migrations.RunPython(move_city_district_into_address, restore_city_district),
        # Geri alırken sütunlar boş varsayılanla yeniden eklenebilsin.
        migrations.AlterField(
            model_name='carerequest',
            name='city',
            field=models.CharField(default='', max_length=50, verbose_name='city'),
        ),
        migrations.AlterField(
            model_name='carerequest',
            name='district',
            field=models.CharField(default='', max_length=50, verbose_name='district'),
        ),
        migrations.RemoveField(
            model_name='carerequest',
            name='city',
        ),
        migrations.RemoveField(
            model_name='carerequest',
            name='district',
        ),
    ]
