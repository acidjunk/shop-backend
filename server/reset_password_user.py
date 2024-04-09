# Copyright 2024 René Dohmen <acidjunk@gmail.com>
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
