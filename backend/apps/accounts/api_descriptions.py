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
    '<p>Refresh tokens are rotated: a new refresh token is returned and the old one must not be reused.</p>'
)

ME_SUMMARY = _('Current user')
ME_VIEW_DESCRIPTION = _(
    '<p>Returns or updates the profile of the authenticated user.</p>'
    '<p>Only name and phone fields can be changed; email and admin rights are read-only.</p>'
)
