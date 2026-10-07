from django.utils.translation import gettext_lazy as _

SERVICE_LIST_SUMMARY = _('List services')
SERVICE_LIST_VIEW_DESCRIPTION = _(
    '<p>Lists the active service types shown in the first step of the request wizard. '
    'No authentication is required.</p>'
    '<p>Results are not paginated and are ordered by <code>sort_order</code>, then name. '
    'Inactive service types are never returned.</p>'
)

CARE_REQUEST_LIST_SUMMARY = _('List my requests')
CARE_REQUEST_LIST_VIEW_DESCRIPTION = _(
    '<p>Lists the care requests of the authenticated applicant, newest first.</p>'
    '<p>Only the requests created by the caller are returned; requests of other users are never visible.</p>'
)

CARE_REQUEST_CREATE_SUMMARY = _('Create request')
CARE_REQUEST_CREATE_VIEW_DESCRIPTION = _(
    '<p>Creates a care request on behalf of an elder. Authentication is required.</p>'
    '<h3>Processing</h3>'
    '<ol>'
    '<li>The caller becomes the applicant of the request.</li>'
    '<li>Phone numbers are normalized to digits.</li>'
    '<li>The consent time is recorded and the request starts with the <code>new</code> status.</li>'
    '</ol>'
    '<h3>Validation rules</h3>'
    '<ul>'
    '<li>An alternate contact name and phone must be given together.</li>'
    '</ul>'
    '<p>Each user can create a limited number of requests per day (<code>care_request_create</code> scope).</p>'
)

CARE_REQUEST_DETAIL_SUMMARY = _('Request detail')
CARE_REQUEST_DETAIL_VIEW_DESCRIPTION = _(
    '<p>Returns one care request of the authenticated applicant.</p>'
    '<p>Requests of other users respond with not found so that their existence is not revealed.</p>'
)

CARE_REQUEST_ID_PARAMETER_DESCRIPTION = _(
    'Identifier of the care request. Copy it from '
    '<a href="#operations-requests-requests_list">List my requests — <code>results[].id</code></a> '
    'or from the <code>id</code> returned by '
    '<a href="#operations-requests-requests_create">Create request</a>.'
)

CARE_REQUEST_SERVICE_HELP_TEXT = _(
    'Identifier of the selected active service type. Copy it from '
    '<a href="#operations-services-services_list">List services — <code>[].id</code></a>.'
)

ADMIN_REQUEST_LIST_SUMMARY = _('Admin: list requests')
ADMIN_REQUEST_LIST_VIEW_DESCRIPTION = _(
    '<p>Lists the care requests of all applicants for the admin panel. Only admin users can call it.</p>'
    '<p>Results are paginated and newest first by default. They can be filtered by status, service, '
    'applicant and creation date range, searched by elder name, applicant email, city, district and phone, '
    'and ordered by creation time, preferred date or status.</p>'
)

ADMIN_FILTER_SERVICE_HELP_TEXT = _(
    'Only requests of this service type. Copy the value from '
    '<a href="#operations-services-services_list">List services — <code>[].id</code></a>.'
)
ADMIN_FILTER_APPLICANT_HELP_TEXT = _(
    'Only requests created by this user. Copy the value from '
    '<a href="#operations-admin-admin_users_list">Admin: list users — <code>results[].id</code></a>.'
)
ADMIN_FILTER_STATUS_HELP_TEXT = _('Only requests in this status.')
ADMIN_FILTER_CREATED_FROM_HELP_TEXT = _('Only requests created on or after this date (YYYY-MM-DD).')
ADMIN_FILTER_CREATED_TO_HELP_TEXT = _('Only requests created on or before this date (YYYY-MM-DD).')

ADMIN_REQUEST_DETAIL_SUMMARY = _('Admin: request detail')
ADMIN_REQUEST_DETAIL_VIEW_DESCRIPTION = _(
    '<p>Returns all details of one care request, including the internal admin note and the statuses '
    'the request can move to. Only admin users can call it.</p>'
)

ADMIN_REQUEST_UPDATE_SUMMARY = _('Admin: update request')
ADMIN_REQUEST_UPDATE_VIEW_DESCRIPTION = _(
    '<p>Changes the status and/or the internal admin note of a care request. Only admin users can call it.</p>'
    '<h3>Validation rules</h3>'
    '<ul>'
    '<li>Status follows the flow <code>new</code> → <code>reviewing</code> → <code>assigned</code> → '
    '<code>completed</code>; any open request can be <code>cancelled</code>.</li>'
    '<li><code>completed</code> and <code>cancelled</code> are final and cannot be changed.</li>'
    '<li>Sending the current status again is allowed, so only the note can be updated.</li>'
    '</ul>'
    '<p>Applicant data cannot be changed from this endpoint.</p>'
)

ADMIN_REQUEST_ID_PARAMETER_DESCRIPTION = _(
    'Identifier of the care request. Copy it from '
    '<a href="#operations-admin-admin_requests_list">Admin: list requests — <code>results[].id</code></a>.'
)

ADMIN_STATS_SUMMARY = _('Admin: dashboard statistics')
ADMIN_STATS_VIEW_DESCRIPTION = _(
    '<p>Returns the summary numbers of the admin dashboard. Only admin users can call it.</p>'
    '<h3>Processing</h3>'
    '<ol>'
    '<li>Requests are counted in total, as open (not completed or cancelled) and for the last 7 days.</li>'
    '<li>Applicants are the active users without admin rights.</li>'
    '<li>Status and service breakdowns list every status and every service type, including zero counts.</li>'
    '<li>The daily series covers the last 14 days including today in the server time zone.</li>'
    '</ol>'
)
