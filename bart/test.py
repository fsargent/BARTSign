import requests
import requests_mock
from bart import BARTSign
from unittest.mock import Mock

mockGraphics = Mock()
mockRequests = requests_mock.Mocker()


self = BARTSign(mockRequests, mockGraphics)
BARTSign.getTrains(self)

print(mockRequests.called)
