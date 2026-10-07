from django.utils.translation import gettext_lazy as _

REGISTER_SUMMARY = _('Register')
REGISTER_VIEW_DESCRIPTION = _(
    '<p>Creates a new applicant account. No authentication is required.</p>'
    '<h3>Processing</h3>'
    '<ol>'
    '<li>The email is normalized to lower case and checked for uniqueness.</li>'
    '<li>The password is checked against the password validators.</li>'
    '<li>The account is created without admin rights.</li>'
    '</ol>'
    '<p>Requests are rate limited per IP address with the <code>accounts_register</code> scope.</p>'
)

TOKEN_OBTAIN_SUMMARY = _('Log in')
TOKEN_OBTAIN_VIEW_DESCRIPTION = _(
    '<p>Returns an access and refresh token pair for valid email and password credentials. '
    'No authentication is required.</p>'
    '<p>Inactive accounts cannot log in. Requests are rate limited per IP address with the '
    '<code>accounts_login</code> scope.</p>'
)

TOKEN_REFRESH_SUMMARY = _('Refresh token')
TOKEN_REFRESH_VIEW_DESCRIPTION = _(
    '<p>Returns a new access token for a valid refresh token. No authentication header is required.</p>'
    '<p>Refresh tokens are rotated: a new refresh token is returned and the old one is blacklisted, '
    'so it cannot be used again.</p>'
)

LOGOUT_SUMMARY = _('Log out')
LOGOUT_VIEW_DESCRIPTION = _(
    '<p>Ends the session on the server by blacklisting the given refresh token. '
    'No authentication header is required.</p>'
    '<p>After logout the refresh token cannot be used again. The short-lived access token expires on its own.</p>'
)

ME_SUMMARY = _('Current user')
ME_VIEW_DESCRIPTION = _(
    '<p>Returns or updates the profile of the authenticated user.</p>'
    '<p>Only name and phone fields can be changed; email and admin rights are read-only.</p>'
)

ADMIN_USER_LIST_SUMMARY = _('Admin: list users')
ADMIN_USER_LIST_VIEW_DESCRIPTION = _(
    '<p>Lists all user accounts with their request counts. Only admin users can call it.</p>'
    '<p>Results are paginated and newest first by default. They can be filtered by admin right and '
    'active state, searched by email, name and phone, and ordered by join date, email or request count.</p>'
)

ADMIN_USER_DETAIL_SUMMARY = _('Admin: user detail')
ADMIN_USER_DETAIL_VIEW_DESCRIPTION = _(
    '<p>Returns one user account with its request count and last login. Only admin users can call it.</p>'
    '<p>The requests of the user can be listed with the admin request list filtered by applicant.</p>'
)

ADMIN_USER_ID_PARAMETER_DESCRIPTION = _(
    'Identifier of the user. Copy it from '
    '<a href="#operations-admin-admin_users_list">Admin: list users — <code>results[].id</code></a>.'
)
