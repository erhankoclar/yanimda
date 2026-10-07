from config.tests.scenario.base import ScenarioTestCase


class RequestLifecycleScenarioTests(ScenarioTestCase):
    def test_full_lifecycle_from_application_to_completion(self):
        """
        Başvurunun oluşturulmasından tamamlanmasına kadar tüm yaşam döngüsünü doğrular.

        Senaryo:
        - Ayşe annesi için refakat hizmetine başvurur.
        - Admin talebi listede görür; inceleniyor, atandı ve tamamlandı adımlarını notlarla ilerletir.
        - Her adımda Ayşe kendi başvurusunun durumuna bakar.

        Beklenti:
        - Ayşe her adımda güncel durumu görmeli, yönetici notunu hiçbir zaman görmemelidir.
        - Tamamlanan talepte başka durum seçeneği kalmamalıdır.
        """
        ayse = self.new_applicant()
        request_id = ayse.apply(self.companion).data['id']
        admin_url = f'/api/admin/requests/{request_id}/'

        listed = self.admin.get('/api/admin/requests/', {'status': 'new'}).data['results']
        self.assertEqual([row['id'] for row in listed], [request_id])

        for step, note in (('reviewing', 'Aile arandı'), ('assigned', 'Bakıcı Zeynep atandı'), ('completed', 'Ziyaret yapıldı')):
            response = self.admin.patch(admin_url, {'status': step, 'admin_note': note})
            self.assertEqual(response.status_code, 200, step)

            seen_by_applicant = ayse.get(f'/api/requests/{request_id}/').data
            self.assertEqual(seen_by_applicant['status'], step)
            self.assertNotIn('admin_note', seen_by_applicant)

        self.assertEqual(self.admin.get(admin_url).data['next_statuses'], [])
        self.assertEqual(self.admin.patch(admin_url, {'status': 'cancelled'}).status_code, 400)

    def test_cannot_apply_twice_for_same_service_and_elder(self):
        """
        Aynı yaşlı için aynı hizmete açık başvuru varken ikinci başvurunun engellendiğini doğrular.

        Senaryo:
        - Ayşe annesi Fatma Yılmaz için refakat başvurusu yapar.
        - Aynı başvuruyu farklı yazımlarla ("FATMA YILMAZ", "fatma yilmaz") tekrar dener.

        Beklenti:
        - Tekrar denemeler 400 dönmeli ve Ayşe'nin tek başvurusu olmalıdır.
        """
        ayse = self.new_applicant()
        ayse.apply(self.companion)

        retries = [ayse.apply(self.companion, elder_full_name=name) for name in ('FATMA YILMAZ', 'fatma yilmaz')]

        self.assertEqual([response.status_code for response in retries], [400, 400])
        self.assertEqual(ayse.get('/api/requests/').data['count'], 1)

    def test_same_family_can_request_for_both_parents_and_other_services(self):
        """
        Aynı kişinin farklı yaşlılar ve farklı hizmetler için başvurabildiğini doğrular.

        Senaryo:
        - Ayşe annesi için refakat, babası için refakat, annesi için hastane eşliği ister.

        Beklenti:
        - Üç başvuru da kabul edilmelidir.
        """
        ayse = self.new_applicant()

        responses = [
            ayse.apply(self.companion),
            ayse.apply(self.companion, elder_full_name='Ahmet Yılmaz'),
            ayse.apply(self.hospital),
        ]

        self.assertEqual([response.status_code for response in responses], [201, 201, 201])

    def test_can_apply_again_after_request_is_completed_or_cancelled(self):
        """
        Önceki başvuru kapandıktan sonra aynı hizmete yeniden başvurulabildiğini doğrular.

        Senaryo:
        - Ayşe başvurur; admin talebi iptal eder; Ayşe yeniden başvurur.
        - Admin yeni talebi sonuna kadar ilerletip tamamlar; Ayşe tekrar başvurur.

        Beklenti:
        - Kapanıştan sonraki her yeniden başvuru kabul edilmeli; toplam üç başvuru görünmelidir.
        """
        ayse = self.new_applicant()
        first_id = ayse.apply(self.companion).data['id']
        self.admin.patch(f'/api/admin/requests/{first_id}/', {'status': 'cancelled'})

        second = ayse.apply(self.companion)
        for step in ('reviewing', 'assigned', 'completed'):
            self.admin.patch(f"/api/admin/requests/{second.data['id']}/", {'status': step})
        third = ayse.apply(self.companion)

        self.assertEqual((second.status_code, third.status_code), (201, 201))
        self.assertEqual(ayse.get('/api/requests/').data['count'], 3)

    def test_admin_cannot_skip_steps_or_reopen_closed_requests(self):
        """
        Yöneticinin durum adımlarını atlayamadığını ve kapanmış talebi yeniden açamadığını doğrular.

        Senaryo:
        - Yeni talep doğrudan tamamlandı yapılmaya çalışılır.
        - Talep iptal edilir, ardından inceleniyor durumuna döndürülmeye çalışılır.

        Beklenti:
        - Atlama ve yeniden açma 400 dönmeli; talep iptal durumunda kalmalıdır.
        """
        ayse = self.new_applicant()
        request_id = ayse.apply(self.companion).data['id']
        url = f'/api/admin/requests/{request_id}/'

        skip = self.admin.patch(url, {'status': 'completed'})
        self.admin.patch(url, {'status': 'cancelled'})
        reopen = self.admin.patch(url, {'status': 'reviewing'})

        self.assertEqual((skip.status_code, reopen.status_code), (400, 400))
        self.assertEqual(ayse.get(f'/api/requests/{request_id}/').data['status'], 'cancelled')

    def test_applicants_never_see_each_others_requests(self):
        """
        İki ailenin birbirinin başvurularını göremediğini, yöneticinin ikisini de gördüğünü doğrular.

        Senaryo:
        - Ayşe ve Mehmet ayrı ayrı başvurur.
        - Her biri kendi listesine ve diğerinin başvuru detayına bakar.

        Beklenti:
        - Listede yalnızca kendi başvurusu olmalı, diğerinin detayı 404 dönmeli; admin iki başvuruyu görmelidir.
        """
        ayse = self.new_applicant('ayse@example.com')
        mehmet = self.new_applicant('mehmet@example.com')
        ayse_id = ayse.apply(self.companion).data['id']
        mehmet_id = mehmet.apply(self.companion).data['id']

        self.assertEqual([row['id'] for row in ayse.get('/api/requests/').data['results']], [ayse_id])
        self.assertEqual(ayse.get(f'/api/requests/{mehmet_id}/').status_code, 404)
        self.assertEqual(mehmet.get(f'/api/requests/{ayse_id}/').status_code, 404)
        self.assertEqual(self.admin.get('/api/admin/requests/').data['count'], 2)

    def test_retired_service_keeps_history_but_blocks_new_applications(self):
        """
        Yayından kaldırılan hizmetin geçmiş başvuruları koruduğunu ama yeni başvuruyu engellediğini doğrular.

        Senaryo:
        - Ayşe refakat hizmetine başvurur; ardından hizmet pasif hale getirilir.
        - Ayşe hizmet listesine ve eski başvurusuna bakar, aynı hizmete başka yaşlı için başvurmayı dener.

        Beklenti:
        - Hizmet listede görünmemeli, eski başvuru görünmeye devam etmeli, yeni başvuru 400 dönmelidir.
        """
        ayse = self.new_applicant()
        request_id = ayse.apply(self.companion).data['id']
        self.companion.is_active = False
        self.companion.save()

        services = [service['id'] for service in ayse.get('/api/services/').data]
        old_request = ayse.get(f'/api/requests/{request_id}/')
        new_request = ayse.apply(self.companion, elder_full_name='Ahmet Yılmaz')

        self.assertNotIn(self.companion.id, services)
        self.assertEqual(old_request.status_code, 200)
        self.assertEqual(new_request.status_code, 400)

    def test_dashboard_reflects_applications_and_status_changes(self):
        """
        Gösterge paneli sayılarının başvurular ve durum değişiklikleriyle birlikte güncellendiğini doğrular.

        Senaryo:
        - İki aile başvurur; admin birini tamamlar.

        Beklenti:
        - Toplam 2, açık 1, başvuru sahibi 2 olmalı; tamamlandı sayısı 1 görünmelidir.
        """
        ayse = self.new_applicant('ayse@example.com')
        mehmet = self.new_applicant('mehmet@example.com')
        ayse_id = ayse.apply(self.companion).data['id']
        mehmet.apply(self.hospital)
        for step in ('reviewing', 'assigned', 'completed'):
            self.admin.patch(f'/api/admin/requests/{ayse_id}/', {'status': step})

        stats = self.admin.get('/api/admin/stats/').data

        self.assertEqual((stats['total_requests'], stats['open_requests'], stats['total_applicants']), (2, 1, 2))
        completed = next(item for item in stats['by_status'] if item['status'] == 'completed')
        self.assertEqual(completed['count'], 1)

    def test_admin_finds_all_requests_of_one_family(self):
        """
        Yöneticinin bir kullanıcıyı bulup tüm başvurularını listeleyebildiğini doğrular.

        Senaryo:
        - Ayşe iki, Mehmet bir başvuru yapar.
        - Admin kullanıcı listesinde Ayşe'yi arar ve kimliğiyle talep listesini filtreler.

        Beklenti:
        - Kullanıcı satırında 2 başvuru görünmeli, filtrelenmiş listede yalnızca Ayşe'nin iki talebi olmalıdır.
        """
        ayse = self.new_applicant('ayse@example.com')
        mehmet = self.new_applicant('mehmet@example.com')
        ayse.apply(self.companion)
        ayse.apply(self.hospital)
        mehmet.apply(self.companion)

        found = self.admin.get('/api/admin/users/', {'search': 'ayse@'}).data['results']
        requests = self.admin.get('/api/admin/requests/', {'applicant': found[0]['id']}).data

        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]['request_count'], 2)
        self.assertEqual(requests['count'], 2)
