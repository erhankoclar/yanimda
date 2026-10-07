from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class InquiryCreateRateThrottle(AnonRateThrottle):
    """Hesapsız hızlı talep formunu IP adresine göre sınırlar."""

    scope = 'care_inquiry_create'


class CareRequestCreateRateThrottle(UserRateThrottle):
    """Kullanıcı başına yeni talep oluşturma sayısını sınırlar."""

    scope = 'care_request_create'

    def allow_request(self, request, view):
        """
        Yalnızca talep oluşturma (POST) isteklerini sınırlar.

        Args:
            request (Request): Gelen istek.
            view (APIView): İsteği işleyen view.

        Returns:
            bool: İsteğe izin veriliyorsa True.
        """
        if request.method != 'POST':
            return True
        return super().allow_request(request, view)
