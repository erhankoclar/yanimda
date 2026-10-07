"""care modülünün varsayılan hizmet türleri."""

DEFAULT_SERVICE_TYPES = [
    {
        'slug': 'evde-bakim',
        'name': 'Evde bakım desteği',
        'description': 'Kişisel bakım, yemek ve günlük işlerde evde destek.',
        'icon': 'home-care',
        'sort_order': 10,
    },
    {
        'slug': 'refakat',
        'name': 'Refakat ve sohbet',
        'description': 'Yalnız kalmasın diye düzenli ziyaret ve sohbet arkadaşlığı.',
        'icon': 'companion',
        'sort_order': 20,
    },
    {
        'slug': 'hastane-esligi',
        'name': 'Hastane ve doktor eşliği',
        'description': 'Randevulara gidiş dönüşte ve muayene sırasında eşlik.',
        'icon': 'hospital',
        'sort_order': 30,
    },
    {
        'slug': 'alisveris-ev-isleri',
        'name': 'Alışveriş ve ev işleri',
        'description': 'Market, eczane alışverişi ve hafif ev işleri.',
        'icon': 'shopping',
        'sort_order': 40,
    },
    {
        'slug': 'saglik-takibi',
        'name': 'Sağlık takibi',
        'description': 'İlaç saatleri, tansiyon ve şeker ölçümü takibi.',
        'icon': 'health',
        'sort_order': 50,
    },
    {
        'slug': 'kucuk-tamir',
        'name': 'Küçük ev tamiri',
        'description': 'Ampul, musluk, priz gibi küçük onarımlar.',
        'icon': 'repair',
        'sort_order': 60,
    },
]
