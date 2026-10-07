import { describe, expect, it } from 'vitest'

import { routes } from '@/router/routes'

/**
 * İç içe route tanımlarını düz listeye çevirir.
 *
 * @param {Array<any>} list Route tanımları.
 * @param {Array<any>} [parents] Üst route zinciri.
 * @returns {Array<{ name?: string, meta: object, parents: Array<any> }>} Düzleştirilmiş route'lar.
 */
function flatten(list, parents = []) {
  return list.flatMap((route) => [
    { ...route, parents },
    ...flatten(route.children ?? [], [...parents, route]),
  ])
}

const flat = flatten(routes)
const byName = (name) => flat.find((route) => route.name === name)

describe('route tablosu', () => {
  it('PRD’deki tüm admin adreslerini tanımlar', () => {
    const adminNames = ['admin-login', 'admin-dashboard', 'admin-users', 'admin-user-detail', 'admin-requests', 'admin-request-detail']

    adminNames.forEach((name) => expect(byName(name), name).toBeDefined())
  })

  it('admin sayfalarını yalnızca admin layout’u altında, admin yetkisiyle tanımlar', () => {
    const adminPages = flat.filter((route) => route.name?.startsWith('admin-') && route.name !== 'admin-login')

    adminPages.forEach((route) => {
      expect(route.parents[0].path, route.name).toBe('/admin')
      expect(route.parents[0].meta.requiresAdmin, route.name).toBe(true)
    })
  })

  it('başvuru sayfalarında giriş zorunluluğu, giriş/kayıt sayfalarında misafir kuralı vardır', () => {
    ;['request-new', 'request-list', 'request-detail'].forEach((name) => {
      expect(byName(name).meta.requiresAuth, name).toBe(true)
    })
    ;['login', 'register', 'admin-login'].forEach((name) => {
      expect(byName(name).meta.guestOnly, name).toBe(true)
    })
  })

  it('tüm sayfa bileşenlerini tembel (lazy) yükler', () => {
    flat.filter((route) => route.component).forEach((route) => {
      expect(typeof route.component, route.name ?? route.path).toBe('function')
    })
  })
})
