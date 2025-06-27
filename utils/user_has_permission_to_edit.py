from static_data.constants import LIST_OF_ALLOWERD_ROLES_TO_EDIT_AND_WHERE

def user_has_permission_to_edit(pathname, user_data):
    role = user_data.get('role_name')
    permission = user_data.get('permission_name')
    ajusted_pathname = pathname.replace("/", "")

    if permission == "WRITE_SOME":
        return True if ajusted_pathname in LIST_OF_ALLOWERD_ROLES_TO_EDIT_AND_WHERE[role] else False
    elif permission == "WRITE_ALL":
        return True
    else:
        return False
