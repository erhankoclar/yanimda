import { computed, useId } from 'vue'

/**
 * Form alanı, ipucu ve hata metni için tutarlı kimlikler ve aria-describedby değeri üretir.
 *
 * @param {() => { hint?: string, error?: string }} source Güncel ipucu ve hata metnini döndüren fonksiyon.
 * @returns {{ inputId: string, hintId: string, errorId: string, describedBy: import('vue').ComputedRef<string | undefined> }}
 *   Alan kimlikleri ve ekran okuyucunun okuyacağı açıklama kimlikleri.
 */
export function useFieldIds(source) {
  const inputId = useId()
  const hintId = `${inputId}-hint`
  const errorId = `${inputId}-error`
  // Hata varsa önce hata, sonra ipucu okunur; ikisi de yoksa öznitelik eklenmez.
  const describedBy = computed(() => {
    const { hint, error } = source()
    return [error && errorId, hint && hintId].filter(Boolean).join(' ') || undefined
  })
  return { inputId, hintId, errorId, describedBy }
}
