from django.contrib.auth import get_user_model

from config.tests.scenario.base import Actor, ScenarioTestCase


class AccountScenarioTests(ScenarioTestCase):
    def test_one_email_belongs_to_exactly_one_account(self):
        """
        Bir e-posta adresinin yalnızca tek bir hesaba ait olabildiğini doğrular.

        Senaryo:
        - Ayşe kayıt olur.
        - Başka biri aynı e-postayla; büyük harfle; baş/son boşluklarla tekrar kayıt olmaya çalışır.

        Beklenti:
        - İlk kayıt 201, diğer üç deneme 400 dönmeli; veritabanında bu e-postayla tek hesap olmalıdır.
        """
        first = Actor('ayse@example.com').register()
        attempts = [
            Actor('ayse@example.com').register(),
            Actor('AYSE@EXAMPLE.COM').register(),
            Actor('  Ayse@Example.com ').register(),
        ]

        self.assertEqual(first.status_code, 201)
        self.assertEqual([response.status_code for response in attempts], [400, 400, 400])
        self.assertEqual(get_user_model().objects.filter(email__iexact='ayse@example.com').count(), 1)

    def test_login_is_by_email_only_without_username(self):
        """
        Girişin yalnızca e-posta ile yapıldığını, kullanıcı adı kavramının olmadığını doğrular.

        Senaryo:
        - Ayşe kayıt olur; kayıt yanıtında ve modelde kullanıcı adı alanı aranır.
        - `username` alanıyla giriş denenir, ardından e-postayla giriş yapılır.

        Beklenti:
        - Hiçbir yerde kullanıcı adı olmamalı; `username` ile giriş 400, e-postayla giriş 200 dönmelidir.
        """
        actor = Actor('ayse@example.com')
        registered = actor.register(username='ayse')

        by_username = actor.client.post('/api/auth/token/', {'username': 'ayse', 'password': actor.password}, format='json')
        by_email = actor.login()

        self.assertNotIn('username', registered.data)
        self.assertIsNone(get_user_model().username)
        self.assertEqual(by_username.status_code, 400)
        self.assertIn('email', by_username.data)
        self.assertEqual(by_email.status_code, 200)

    def test_login_accepts_email_typed_differently(self):
        """
        Kullanıcının e-postasını büyük harfle veya boşlukla yazsa da giriş yapabildiğini doğrular.

        Senaryo:
        - Ayşe küçük harfli e-postayla kayıt olur, ardından `  AYSE@Example.COM ` yazarak giriş yapar.

        Beklenti:
        - Giriş 200 dönmeli ve profil doğru hesabı göstermelidir.
        """
        actor = Actor('ayse@example.com')
        actor.register()

        response = actor.login(email='  AYSE@Example.COM ')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(actor.get('/api/auth/me/').data['email'], 'ayse@example.com')

    def test_new_account_starts_with_no_requests_and_no_admin_rights(self):
        """
        Yeni hesabın boş başvuru listesiyle ve admin yetkisi olmadan başladığını doğrular.

        Senaryo:
        - Yeni başvuru sahibi kayıt olup giriş yapar; başvurularını ve admin panelini açar.

        Beklenti:
        - Başvuru listesi boş olmalı, profilde `is_staff` False olmalı, admin endpoint'i 403 dönmelidir.
        """
        applicant = self.new_applicant()

        self.assertEqual(applicant.get('/api/requests/').data['count'], 0)
        self.assertFalse(applicant.get('/api/auth/me/').data['is_staff'])
        self.assertEqual(applicant.get('/api/admin/requests/').status_code, 403)

    def test_wrong_password_never_reveals_whether_email_exists(self):
        """
        Hatalı parola ile kayıtlı olmayan e-postanın aynı yanıtı verdiğini doğrular (hesap keşfi koruması).

        Senaryo:
        - Kayıtlı e-postayla yanlış parola, ardından hiç kayıtlı olmayan e-postayla giriş denenir.

        Beklenti:
        - İki yanıt da 401 ve aynı hata gövdesine sahip olmalıdır.
        """
        Actor('ayse@example.com').register()

        wrong_password = Actor('ayse@example.com').login(password='yanlis-parola')
        unknown_email = Actor('kimse@example.com').login()

        self.assertEqual(wrong_password.status_code, 401)
        self.assertEqual(unknown_email.status_code, 401)
        self.assertEqual(wrong_password.data, unknown_email.data)

    def test_disabled_account_loses_access_immediately(self):
        """
        Pasif hale getirilen hesabın açık oturumunun da hemen geçersiz olduğunu doğrular.

        Senaryo:
        - Başvuru sahibi giriş yapar; ardından hesap pasif hale getirilir.
        - Mevcut token ile profil istenir ve yeniden giriş denenir.

        Beklenti:
        - Profil isteği 401, yeniden giriş 401 dönmelidir.
        """
        applicant = self.new_applicant()
        get_user_model().objects.filter(email='ayse@example.com').update(is_active=False)

        self.assertEqual(applicant.get('/api/auth/me/').status_code, 401)
        self.assertEqual(Actor('ayse@example.com').login().status_code, 401)

    def test_logout_ends_the_session_for_good(self):
        """
        Çıkış yapıldıktan sonra oturumun yenilenemediğini doğrular.

        Senaryo:
        - Başvuru sahibi giriş yapar ve çıkış yapar.
        - Eski refresh token ile oturum yenilenmeye çalışılır.

        Beklenti:
        - Yenileme 401 dönmelidir.
        """
        applicant = self.new_applicant()
        applicant.client.post('/api/auth/logout/', {'refresh': applicant.refresh}, format='json')

        response = applicant.client.post('/api/auth/token/refresh/', {'refresh': applicant.refresh}, format='json')

        self.assertEqual(response.status_code, 401)

    def test_profile_update_cannot_take_over_another_email(self):
        """
        Profil güncellemesiyle başka birinin e-postasına geçilemediğini doğrular (hesap ele geçirme).

        Senaryo:
        - Ayşe ve Mehmet kayıt olur; Mehmet profilinde e-postasını Ayşe'ninki yapmaya çalışır.

        Beklenti:
        - Mehmet'in e-postası değişmemeli ve Ayşe'nin hesabı etkilenmemelidir.
        """
        self.new_applicant('ayse@example.com')
        mehmet = self.new_applicant('mehmet@example.com')

        mehmet.patch('/api/auth/me/', {'email': 'ayse@example.com'})

        self.assertEqual(mehmet.get('/api/auth/me/').data['email'], 'mehmet@example.com')
        self.assertEqual(get_user_model().objects.filter(email='ayse@example.com').count(), 1)
