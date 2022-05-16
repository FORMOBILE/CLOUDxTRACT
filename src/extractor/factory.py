class ExtractorFactory:
    def __init__(self) -> None:
        self._services = {}

    def register_service(self, service_name, creator) -> None:
        self._services[service_name] = creator

    @classmethod
    def get_extractor(cls, service, config={}, **kargs):
        if not service:
            raise ValueError(service)

        

    
