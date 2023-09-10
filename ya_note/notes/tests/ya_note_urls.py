from django.urls import reverse


# Routes
NOTES_EDIT_ROUTE = 'notes:edit'
NOTES_ADD_ROUTE = 'notes:add'
NOTES_DELETE_ROUTE = 'notes:delete'
NOTES_HOME_ROUTE = 'notes:home'
NOTES_LOGIN_ROUTE = 'users:login'
NOTES_LOGOUT_ROUTE = 'users:logout'
NOTES_SIGNUP_ROUTE = 'users:signup'
NOTES_DETAIL_ROUTE = 'notes:detail'
NOTES_SUCCESS_ROUTE = 'notes:success'
NOTES_LIST_ROUTE = 'notes:list'
# URLs
NOTES_LIST_URL = reverse(NOTES_LIST_ROUTE)
NOTES_LOGIN_URL = reverse(NOTES_LOGIN_ROUTE)
NOTES_SUCCESS_URL = reverse(NOTES_SUCCESS_ROUTE)
NOTES_ADD_URL = reverse(NOTES_ADD_ROUTE)
