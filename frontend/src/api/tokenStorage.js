// JWT çiftini tarayıcıda saklar. Gizli pencere veya engellenmiş depolama
// durumunda erişim hata verebileceğinden her işlem try/catch içindedir.
const ACCESS_KEY = 'yanimda.access'
const REFRESH_KEY = 'yanimda.refresh'

/**
 * localStorage'dan güvenli şekilde değer okur.
 *
 * @param {string} key Anahtar.
 * @returns {string | null} Değer; yoksa veya depolama erişilemezse null.
 */
function read(key) {
  try {
    return window.localStorage.getItem(key)
  } catch {
    return null
  }
}

/**
 * localStorage'a güvenli şekilde değer yazar veya null ise siler.
 *
 * @param {string} key Anahtar.
 * @param {string | null} value Yazılacak değer.
 */
function write(key, value) {
  try {
    if (value) window.localStorage.setItem(key, value)
    else window.localStorage.removeItem(key)
  } catch {
    // Depolama kullanılamıyorsa oturum yalnızca sayfa açıkken sürer.
  }
}

export const tokenStorage = {
  getAccess: () => read(ACCESS_KEY),
  getRefresh: () => read(REFRESH_KEY),
  /**
   * Token çiftini kaydeder; refresh verilmezse mevcut refresh korunur.
   *
   * @param {{ access: string, refresh?: string }} tokens Token çifti.
   */
  set({ access, refresh }) {
    write(ACCESS_KEY, access)
    if (refresh) write(REFRESH_KEY, refresh)
  },
  clear() {
    write(ACCESS_KEY, null)
    write(REFRESH_KEY, null)
  },
}
