import pytest
from unittest.mock import patch, call, PropertyMock

from ..main import VirtualMachine


@pytest.fixture
def empty_vm():
    """Returns a VirtualMachine with no queued messages."""
    queues = [[], [], []]
    # Patch `empty_queue`, `send_message`, and 'write_to_log` instance methods
    # We need to handle `empty_queue` differently because of the @property decorator 
    with patch.object(VirtualMachine, 'empty_queue', new_callable=PropertyMock) as mock_empty_queue, \
        patch.object(VirtualMachine, 'send_message', return_value=None), \
        patch.object(VirtualMachine, 'write_to_log', return_value=None):
        mock_empty_queue.return_value = True
        yield VirtualMachine(0, queues)


def test_update_lclock_internal(empty_vm):
    """Test the case where `update_lclock` is called without another clock time argument."""
    empty_vm.update_lclock()
    assert empty_vm.lclock == 1


def test_update_lclock_local_large(empty_vm):
    """
    Test the case where `update_lclock` is called with another clock time, where
    the local logical clock time is larger.
    """
    empty_vm.lclock = 5
    empty_vm.update_lclock(recv_clock=3)
    assert empty_vm.lclock == 6


def test_update_lclock_local_small(empty_vm):
    """
    Test the case where `update_lclock` is called with another clock time, where
    the local logical clock time is smaller.
    """
    empty_vm.lclock = 2
    empty_vm.update_lclock(recv_clock=3)
    assert empty_vm.lclock == 4
    

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
    """
    Simulate one clock cycle where there are no queued messages
    and the dice roll results in an internal event.
    """
    mock_random.return_value = 5
    empty_vm.step()

    # Check that `write_to_log` is called for internal event
    log_args = empty_vm.write_to_log.call_args[0]
    assert len(log_args) == 1
    assert log_args[0].startswith("Internal event")

    # Check that the logical clock value is correct
    assert empty_vm.lclock == 1
    

def test_step_with_msg():
    """Test the case where `step()` is called with a queued message."""
    # Patch `empty_queue`, `pop_message`, and `write_to_log` instance methods
    with patch.object(VirtualMachine, 'empty_queue', new_callable=PropertyMock) as mock_empty_queue, \
        patch.object(VirtualMachine, 'pop_message', return_value=3), \
        patch.object(VirtualMachine, 'write_to_log', return_value=None):
        # Set `empty_queue` property to False
        mock_empty_queue.return_value = False
        # We pass `queues=None` since it is not accessed
        vm = VirtualMachine(1, None)
        vm.step()
    
        # Check that `write_to_log` is called correctly
        log_args = vm.write_to_log.call_args[0]
        assert len(log_args) == 1
        assert log_args[0].startswith(f"Received message")

        # The logical clock value should now be 4
        assert vm.lclock == 4




