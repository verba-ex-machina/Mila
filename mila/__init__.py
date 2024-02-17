"""Provide the Mila framework."""

from .module.fake import FakeIO


class MilaIO(FakeIO):
    """Define the Mila TaskIO handler."""

    # For now we're using the fake as an echo server.
