"""care modülünün varsayılan hizmet türleri; ad ve açıklama dil başına `translations` altında verilir."""

DEFAULT_SERVICE_TYPES = [
    {
        'slug': 'evde-bakim',
        'translations': {
            'tr': {'name': 'Evde bakım desteği', 'description': 'Kişisel bakım, yemek ve günlük işlerde evde destek.'},
            'en': {'name': 'Home care support', 'description': 'Personal care, meals and help with daily tasks at home.'},
        },
        'icon': 'home-care',
        'sort_order': 10,
    },
    {
        'slug': 'refakat',
        'translations': {
            'tr': {'name': 'Refakat ve sohbet', 'description': 'Yalnız kalmasın diye düzenli ziyaret ve sohbet arkadaşlığı.'},
            'en': {'name': 'Companionship and conversation', 'description': 'Regular visits and conversation so they are not left alone.'},
        },
        'icon': 'companion',
        'sort_order': 20,
    },
    {
        'slug': 'hastane-esligi',
        'translations': {
            'tr': {'name': 'Hastane ve doktor eşliği', 'description': 'Randevulara gidiş dönüşte ve muayene sırasında eşlik.'},
            'en': {'name': 'Hospital and doctor escort', 'description': 'Company on the way to appointments and during examinations.'},
        },
        'icon': 'hospital',
        'sort_order': 30,
    },
    {
        'slug': 'alisveris-ev-isleri',
        'translations': {
            'tr': {'name': 'Alışveriş ve ev işleri', 'description': 'Market, eczane alışverişi ve hafif ev işleri.'},
            'en': {'name': 'Shopping and housework', 'description': 'Grocery and pharmacy shopping and light housework.'},
        },
        'icon': 'shopping',
        'sort_order': 40,
    },
    {
        'slug': 'saglik-takibi',
        'translations': {
            'tr': {'name': 'Sağlık takibi', 'description': 'İlaç saatleri, tansiyon ve şeker ölçümü takibi.'},
            'en': {'name': 'Health monitoring', 'description': 'Tracking medication times, blood pressure and blood sugar.'},
        },
        'icon': 'health',
        'sort_order': 50,
    },
    {
        'slug': 'kucuk-tamir',
        'translations': {
            'tr': {'name': 'Küçük ev tamiri', 'description': 'Ampul, musluk, priz gibi küçük onarımlar.'},
            'en': {'name': 'Small home repairs', 'description': 'Small fixes such as light bulbs, taps and sockets.'},
        },
        'icon': 'repair',
        'sort_order': 60,
    },
]
