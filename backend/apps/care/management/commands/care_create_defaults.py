from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy

from apps.care.defaults import DEFAULT_SERVICE_TYPES
from apps.care.models import ServiceType

LINE_WIDTH = 78


class Command(BaseCommand):
    help = gettext_lazy('Creates or updates the default data of the care module.')

    def handle(self, *args, **options):
        """
        care modülünün varsayılan veri gruplarını sırayla kurar ve sayaçları raporlar.

        Args:
            *args (Any): Django'nun ilettiği konumsal argümanlar.
            **options (Any): Komut seçenekleri.

        Raises:
            Exception: Herhangi bir veri grubu başarısız olduğunda, çıktı kapatıldıktan sonra yeniden fırlatılır.
        """
        steps = [
            (gettext('Service types'), self._create_service_types),
        ]
        total = len(steps)
        created_total = 0
        updated_total = 0

        self.stdout.write('*' * LINE_WIDTH)
        self.stdout.write(gettext('CARE DEFAULT DATA SETUP STARTED'))
        try:
            for index, (label, step) in enumerate(steps, start=1):
                self.stdout.write('-' * LINE_WIDTH)
                prefix = f'[{index}/{total}]'
                self.stdout.write(gettext('%(prefix)s %(label)s started.') % {'prefix': prefix, 'label': label})
                result = step()
                created_total += result['created']
                updated_total += result['updated']
                self.stdout.write(gettext('%(prefix)s %(label)s completed. Created: %(created)d, Updated: %(updated)d.') % {
                    'prefix': prefix, 'label': label, 'created': result['created'], 'updated': result['updated'],
                })
        except Exception as error:
            self.stdout.write('-' * LINE_WIDTH)
            self.stderr.write(gettext('Care default data setup failed: %(error)s') % {'error': error})
            self.stdout.write('*' * LINE_WIDTH)
            raise

        self.stdout.write('-' * LINE_WIDTH)
        self.stdout.write(gettext('All care default data operations completed. Created: %(created)d, Updated: %(updated)d.') % {
            'created': created_total, 'updated': updated_total,
        })
        self.stdout.write('*' * LINE_WIDTH)

    @transaction.atomic
    def _create_service_types(self):
        """
        Varsayılan hizmet türlerini slug'a göre oluşturur, değişmiş olanları günceller.

        Değeri aynı olan mevcut kayıtlara dokunulmaz; bu nedenle komut tekrar
        çalıştırılabilir.

        Returns:
            dict[str, int]: `created` ve `updated` kayıt sayıları.
        """
        created = 0
        updated = 0
        for data in DEFAULT_SERVICE_TYPES:
            fields = {key: value for key, value in data.items() if key != 'slug'}
            service, was_created = ServiceType.objects.get_or_create(slug=data['slug'], defaults=fields)
            if was_created:
                created += 1
                continue
            changed = [key for key, value in fields.items() if getattr(service, key) != value]
            if changed:
                for key in changed:
                    setattr(service, key, fields[key])
                service.save(update_fields=changed)
                updated += 1
        return {'created': created, 'updated': updated}
