"""Decorators for Pagination."""

from typing import Any, Sequence, Tuple, Iterator
from functools import singledispatchmethod

from aries_cloudagent.messaging.models.base import BaseModel
from marshmallow import fields

from ..util import expand_model_class


@expand_model_class
class Page(BaseModel):
    """Page decorator for messages containing a paginated object."""

    class Fields:
        """Fields of page decorator."""
        count = fields.Int(required=True)
        offset = fields.Int(required=True)
        remaining = fields.Int(required=False)

    def __init__(
        self, count: int = 0, offset: int = 0, remaining: int = None, **kwargs
    ):
        super().__init__(**kwargs)
        self.count = count
        self.offset = offset
        self.remaining = remaining


@expand_model_class
class Paginate(BaseModel):
    """Paginate decorator for messages querying for a paginated object."""

    class Fields:
        """Fields of paginate decorator."""
        limit = fields.Int(required=True)
        offset = fields.Int(required=True, missing=0)

    def __init__(self, limit: int = 0, offset: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.limit = limit
        self.offset = offset

    @singledispatchmethod
    def apply(self, items) -> Tuple[Sequence[Any], Page]:
        """Apply pagination, returning paginated results and Page decorator."""
        raise NotImplementedError(
            "Paginate.apply is not implemented for type {}".format(type(items))
        )

    @apply.register
    def apply(self, items: list) -> Tuple[Sequence[Any], Page]:
        """Apply pagination to list."""
        end = self.offset + self.limit
        result = items[self.offset:end]
        remaining = len(items[end:])
        page = Page(len(result), self.offset, remaining)
        return result, page

    @apply.register
    def apply(self, items: Iterator) -> Tuple[Sequence[Any], Page]:
        """Apply pagination to iterator."""
        for _, _ in zip(range(self.offset), items):
            pass

        result = []
        for _idx, item in zip(range(self.offset, self.offset + self.limit), items):
            result.append(item)

        page = Page(len(result), self.offset)
        return result, page
