import pytest
from unittest.mock import patch, call

from ..main import VirtualMachine


@pytest.fixture
def empty_vm():
    """Returns a VirtualMachine with no queued messages."""
    queues = [[], [], []]
    # Patch `empty_queue`, `send_message`, and 'write_to_log` instance methods
    with patch.object(VirtualMachine, 'empty_queue', return_value=True), \
        patch.object(VirtualMachine, 'send_message', return_value=None), \
        patch.object(VirtualMachine, 'write_to_log', ):
        yield VirtualMachine(0, queues)


@patch('random.randint')
def test_step1(mock_random, empty_vm):
    """
    Simulate one clock cycle where there are no queued messages and
    and the dice roll is 1.
    """
    mock_random.return_value = 1
    empty_vm.step()
    
    # Check the values that `send_message` is called with
    exp_msg_args = (1, '0')
    actual_msg_args = empty_vm.send_message.call_args[0]
    assert exp_msg_args == actual_msg_args

    # Check that the logical clock value is correct
    assert empty_vm.lclock == 1
    

@patch('random.randint')
def test_step2(mock_random, empty_vm):
    """
    Simulate one clock cycle where there are no queued messages and
    and the dice roll is 2.
    """
    mock_random.return_value = 2
    empty_vm.step()
    
    # Check the values that `send_message` is called with
    exp_msg_args = (2, '0')
    actual_msg_args = empty_vm.send_message.call_args[0]
    assert exp_msg_args == actual_msg_args

    # Check that the logical clock value is correct
    assert empty_vm.lclock == 1
    

@patch('random.randint')
def test_step3(mock_random, empty_vm):
    """
    Simulate one clock cycle where there are no queued messages and
    and the dice roll is 3.
    """
    mock_random.return_value = 3
    empty_vm.step()
    
    # Check that `send_message` is called twice with these values
    exp_msg_args = [call(1, '0'), call(2, '0')]
    empty_vm.send_message.assert_has_calls(exp_msg_args)

    # Check that the logical clock value is correct
    assert empty_vm.lclock == 1


@patch('random.randint')
def test_step_internal(mock_random, empty_vm):
    assert True
