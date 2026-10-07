from django.core.management.base import BaseCommand
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy

from apps.care.services import service_type_service

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
            (gettext('Service types'), service_type_service.create_default_service_types),
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
