from unittest.mock import Mock
from testing_training.machine.buyer_app.engines_controller import EnginesController


def test_can_be_opened_and_closed():
    engines_controller = EnginesController()
    mock = Mock()
    engines_controller._serial = mock

    engines_controller.open()
    engines_controller.close()

    mock.open.assert_called_once()
    mock.closed.assert_called_once()
