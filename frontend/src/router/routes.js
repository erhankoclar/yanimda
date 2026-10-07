// Son kullanıcı ve admin route'ları ayrı layout'lar altında tutulur; admin
// tarafının tüm bileşenleri ayrı (lazy) chunk'larda yüklenir.
export const routes = [
  {
    path: '/',
    component: () => import('@/layouts/PublicLayout.vue'),
    children: [
      { path: '', name: 'landing', component: () => import('@/views/public/LandingView.vue') },
      { path: 'login', name: 'login', component: () => import('@/views/public/LoginView.vue'), meta: { guestOnly: true } },
      { path: 'register', name: 'register', component: () => import('@/views/public/RegisterView.vue'), meta: { guestOnly: true } },
      { path: 'requests/new', name: 'request-new', component: () => import('@/views/public/NewRequestView.vue'), meta: { requiresAuth: true } },
      { path: 'requests', name: 'request-list', component: () => import('@/views/public/RequestListView.vue'), meta: { requiresAuth: true } },
      { path: 'requests/:id(\\d+)', name: 'request-detail', component: () => import('@/views/public/RequestDetailView.vue'), meta: { requiresAuth: true }, props: true },
    ],
  },
  {
    path: '/admin/login',
    name: 'admin-login',
    component: () => import('@/views/admin/AdminLoginView.vue'),
    meta: { guestOnly: true, area: 'admin' },
  },
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAdmin: true, area: 'admin' },
    children: [
      { path: '', redirect: { name: 'admin-dashboard' } },
      { path: 'dashboard', name: 'admin-dashboard', component: () => import('@/views/admin/DashboardView.vue') },
      { path: 'users', name: 'admin-users', component: () => import('@/views/admin/UsersView.vue') },
      { path: 'users/:id(\\d+)', name: 'admin-user-detail', component: () => import('@/views/admin/UserDetailView.vue'), props: true },
      { path: 'requests', name: 'admin-requests', component: () => import('@/views/admin/RequestsView.vue') },
      { path: 'requests/:id(\\d+)', name: 'admin-request-detail', component: () => import('@/views/admin/RequestDetailView.vue'), props: true },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    component: () => import('@/layouts/PublicLayout.vue'),
    children: [{ path: '', name: 'not-found', component: () => import('@/views/public/NotFoundView.vue') }],
  },
]
