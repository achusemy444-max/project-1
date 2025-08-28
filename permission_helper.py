from android.permissions import Permission, request_permissions, check_permission

def request_storage_permission():
    permissions = [
        Permission.WRITE_EXTERNAL_STORAGE, 
        Permission.READ_EXTERNAL_STORAGE
    ]
    has_permissions = all(
        check_permission(permission) for permission in permissions
    )
    if not has_permissions:
        request_permissions(permissions)
        return False
    return True

def request_camera_permission():
    if not check_permission(Permission.CAMERA):
        request_permissions([Permission.CAMERA])
        return False
    return True
