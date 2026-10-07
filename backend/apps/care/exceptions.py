"""care servislerinin fırlattığı iş kuralı hataları."""


class CareRuleError(Exception):
    """
    Bir iş kuralı ihlal edildiğinde fırlatılır.

    `field`, hatanın gösterileceği alanı; `message`, kullanıcıya gösterilecek
    çevrilmiş metni taşır. View katmanı bunu doğrulama hatasına çevirir.
    """

    def __init__(self, field, message):
        """
        Hatayı alan ve mesajla oluşturur.

        Args:
            field (str): Hatanın ait olduğu alan.
            message (str): Çevrilmiş hata mesajı.
        """
        super().__init__(message)
        self.field = field
        self.message = message


class DuplicateOpenRequestError(CareRuleError):
    """Aynı yaşlı için aynı hizmette açık başvuru varken yenisi açılmak istendiğinde."""


class InvalidStatusTransitionError(CareRuleError):
    """Başvuru izin verilmeyen bir duruma taşınmak istendiğinde."""
