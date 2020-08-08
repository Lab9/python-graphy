class Settings:
    """
    A Settings object holds necessary settings for the graphy library to work.
    Each setting can be changed but do this with caution.
    """

    def __init__(
            self,
            max_recursion_depth=2,
            base_response_key="data",
            return_requests_response=False
    ):
        """
        Instantiate a new Settings instance to be used by a client.

        :param max_recursion_depth: holds the max depth for looking up return fields when no selection is passed by.
        :param base_response_key: holds the base response key. This is probably "data" in most cases.
        :param return_requests_response: True if you want the requests response object. If False will try to parse json.
        """
        self.max_recursion_depth = max_recursion_depth
        self.default_response_key = base_response_key
        self.return_requests_response = return_requests_response
