from django.test import TestCase

from apps.care.factories import CareRequestFactory, ServiceInquiryFactory


class CareFactoryNameTests(TestCase):
    def test_generated_names_have_two_parts_without_titles(self):
        """
        Fabrikaların ürettiği kişi adlarının unvansız ad ve soyaddan oluştuğunu doğrular.

        Senaryo:
        - Birkaç hızlı talep ve başvuru fabrikayla üretilir.

        Beklenti:
        - Her ad tam iki parçadan oluşmalı ve nokta içeren unvan (ör. "Dr.") barındırmamalıdır.
        """
        names = [ServiceInquiryFactory().full_name for _index in range(5)]
        names += [CareRequestFactory().elder_full_name for _index in range(5)]

        for name in names:
            self.assertEqual(len(name.split()), 2, name)
            self.assertNotIn('.', name)
