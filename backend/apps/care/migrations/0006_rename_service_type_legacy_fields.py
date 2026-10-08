from django.db import migrations


class Migration(migrations.Migration):
    """
    Hizmet adı ve açıklamasının eski sütunlarını yeniden adlandırır.

    django-parler aynı adlı model alanı dururken çeviri alanı eklemeye izin vermez; veri
    kaybolmasın diye sütunlar silinmez, adları değiştirilir ve sonraki migration'da
    çeviri tablosuna kopyalanır.
    """

    dependencies = [
        ('care', '0005_service_type_english'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='servicetype',
            options={'ordering': ['sort_order', 'slug'], 'verbose_name': 'service type', 'verbose_name_plural': 'service types'},
        ),
        migrations.RenameField(model_name='servicetype', old_name='name', new_name='legacy_name'),
        migrations.RenameField(model_name='servicetype', old_name='description', new_name='legacy_description'),
    ]
