from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy

from apps.care.services import demo_data_service

LINE_WIDTH = 78


class Command(BaseCommand):
    help = gettext_lazy(
        'Creates fictional demo inquiries and applications for the last days. Runs only with DEBUG enabled.'
    )

    def add_arguments(self, parser):
        """
        Komut seçeneklerini tanımlar.

        Args:
            parser (argparse.ArgumentParser): Django'nun komut ayrıştırıcısı.
        """
        parser.add_argument('--days', type=int, default=90, help=gettext_lazy('Number of past days to fill.'))
        parser.add_argument(
            '--reset', action='store_true', help=gettext_lazy('Delete the existing demo data and create it again.'),
        )

    def handle(self, *args, **options):
        """
        Demo verisini (gerekirse önce silerek) üretir ve sayaçları raporlar.

        Args:
            *args (Any): Django'nun ilettiği konumsal argümanlar.
            **options (Any): `days` ve `reset` seçenekleri.

        Raises:
            CommandError: DEBUG kapalıyken çalıştırıldığında; canlı veritabanına kurgusal kayıt yazılmaz.
            Exception: Veri üretimi başarısız olduğunda, çıktı kapatıldıktan sonra yeniden fırlatılır.
        """
        if not settings.DEBUG:
            raise CommandError(gettext('Demo data can only be created when DEBUG is enabled.'))

        steps = []
        if options['reset']:
            steps.append((gettext('Existing demo data removal'), self._remove))
        steps.append((gettext('Demo inquiries and applications'), lambda: demo_data_service.create_demo_data(
            days=options['days'],
        )))
        total = len(steps)
        created_total = 0
        updated_total = 0

        self.stdout.write('*' * LINE_WIDTH)
        self.stdout.write(gettext('CARE DEMO DATA SETUP STARTED'))
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
            self.stderr.write(gettext('Care demo data setup failed: %(error)s') % {'error': error})
            self.stdout.write('*' * LINE_WIDTH)
            raise

        self.stdout.write('-' * LINE_WIDTH)
        self.stdout.write(gettext('All care demo data operations completed. Created: %(created)d, Updated: %(updated)d.') % {
            'created': created_total, 'updated': updated_total,
        })
        self.stdout.write('*' * LINE_WIDTH)

    def _remove(self):
        """
        Mevcut demo verisini siler ve silinen satır sayısını raporlar.

        Returns:
            dict[str, int]: Sayaç yapısına uymak için `created` ve `updated` her zaman 0'dır.
        """
        removed = demo_data_service.remove_demo_data()
        self.stdout.write(gettext('Removed rows: %(count)d.') % {'count': removed})
        return {'created': 0, 'updated': 0}
