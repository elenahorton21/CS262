import pytest

from ..main import VirtualMachine

@pytest.fixture
def vm():
    # TODO: Use mocks for queues?
    queues = [[], [], []]
    return VirtualMachine(0, queues)

def test_av(vm):
    pass