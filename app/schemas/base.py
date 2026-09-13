from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Accepts snake_case or camelCase in, always emits camelCase out."""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)
