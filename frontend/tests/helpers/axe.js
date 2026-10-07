import axe from 'axe-core'

/**
 * Verilen DOM öğesinde axe-core erişilebilirlik denetimini çalıştırır.
 *
 * jsdom renk hesaplayamadığından kontrast kuralı kapatılır; kontrast tarayıcı
 * tabanlı testlerde denetlenir.
 *
 * @param {Element} element Denetlenecek kök öğe.
 * @returns {Promise<Array<{ id: string, help: string, nodes: Array<{ html: string }> }>>} İhlaller.
 */
export async function axeViolations(element) {
  const result = await axe.run(element, {
    rules: { 'color-contrast': { enabled: false } },
  })
  return result.violations.map(({ id, help, nodes }) => ({ id, help, nodes: nodes.map(({ html }) => ({ html })) }))
}
