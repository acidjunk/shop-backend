# Copyright 2026 René Dohmen <acidjunk@gmail.com>
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
from typing import Optional
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel


class ProductAttributeItem(BoilerplateBaseModel):
    """Lightweight representation of a product's attribute value used in responses.

    - attribute_id: the AttributeTable id
    - attribute_name: translated main_name for display (optional, may be omitted in some endpoints)
    - option_id: the AttributeOptionTable id when the value is an enum option
    - option_value_key: the option key (e.g., "XS", "M") when applicable
    - value_text: free-form string value when not using an option
    """

    attribute_id: UUID
    attribute_name: Optional[str] = None
    option_id: Optional[UUID] = None
    option_value_key: Optional[str] = None
    value_text: Optional[str] = None
