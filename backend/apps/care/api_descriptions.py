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
