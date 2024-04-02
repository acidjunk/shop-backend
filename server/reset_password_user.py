from fastapi import HTTPException

from server.crud.crud_user import user_crud
from server.schemas import UserUpdate


def reset_password(new_password, email):
    """
    Reset password
    """
    user = user_crud.get_by_email(email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    elif not user_crud.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    updated_user = UserUpdate(password=new_password)
    user_crud.update(db_obj=user, obj_in=updated_user)
    return "Password updated successfully"


if __name__ == "__main__":
    print("Enter user email:")
    user_email = str(input())
    print("Enter new password:")
    password = str(input())
    reset_password(password, user_email)
