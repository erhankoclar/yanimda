// Başvuru durumlarının admin arayüzündeki görünümü; tablo etiketleri ve grafik aynı renkleri kullanır.
export const STATUS_STYLES = {
  new: { severity: 'info', color: '#4a8fd6' },
  reviewing: { severity: 'warn', color: '#f29e4c' },
  // PrimeVue'da mor tonlu önem derecesi yok; `info` taban alınıp `status-tag--assigned` sınıfıyla renklenir.
  assigned: { severity: 'info', color: '#a46bc0' },
  completed: { severity: 'success', color: '#2e9c8a' },
  cancelled: { severity: 'secondary', color: '#9aa5a1' },
}

/**
 * Durumun PrimeVue Tag önem derecesini döndürür.
 *
 * @param {string} status Başvuru durumu.
 * @returns {string} Tag `severity` değeri; bilinmeyen durumda `secondary`.
 */
export function statusSeverity(status) {
  return STATUS_STYLES[status]?.severity ?? 'secondary'
}

/**
 * Durum etiketine eklenecek sınıfı döndürür; tüm durumlar aynı pastel etiket biçimini kullanır.
 *
 * @param {string} status Başvuru durumu.
 * @returns {string} CSS sınıfı.
 */
export function statusClass(status) {
  return `status-tag status-tag--${status}`
}

/**
 * Durumun grafik rengini döndürür.
 *
 * @param {string} status Başvuru durumu.
 * @returns {string} Renk kodu; bilinmeyen durumda gri.
 */
export function statusColor(status) {
  return STATUS_STYLES[status]?.color ?? '#9aa5a1'
}
