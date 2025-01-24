from pyflowlauncher import Plugin, Result, Method, api as API
from pyflowlauncher.result import ResultResponse
import re

class Query(Method):
    def __init__(self, plugin: Plugin) -> None:
        super().__init__()
        self.plugin = plugin

        self.service = self.plugin.settings.get("service")
        self.log_level = self.plugin.settings.get("log_level")
        self.prompt_stop = "||"

        if self.log_level:
            self.plugin._logger.setLevel(self.log_level)
    
    def __call__(self, query: str) -> ResultResponse:
        try:
            if not query:
                title = f"Insert URL"
                message = f"e.g. https://example.com"
            
                self.add_result(Result(
                    Title=title,
                    SubTitle=message,
                    IcoPath=self.plugin.manifest().get("IcoPath")
                ))
            else:
                if self.service:
                    # Validate URL with protocol
                    url_pattern = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
                    url_match = re.match(url_pattern, query)
                    
                    if not url_match:
                        # Validate URL without protocol
                        url_pattern = "^[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
                        url_match = re.match(url_pattern, query)
                        
                        if not url_match:
                            title = f"Please insert a valid URL"
                            message = f"{query}"
                
                            self.add_result(Result(
                                            Title=title,
                                            SubTitle=message,
                                            IcoPath=self.plugin.manifest().get("IcoPath")
                            ))

                    if url_match:
                        remove_paywall_url = self.service + query
                        title = f"Open URL"
                        message = f"Open URL in default Browser: {remove_paywall_url}"
                        json_rpc_action = API.open_url(remove_paywall_url)
                    
                        self.add_result(Result(
                                        Title=title,
                                        SubTitle=message,
                                        JsonRPCAction=json_rpc_action,
                                        IcoPath=self.plugin.manifest().get("IcoPath")
                        ))
                else:
                    title = f"ERROR"
                    message = f"Error: No Service for the Paywall removal is set <{self.service}>"
                    json_rpc_action = API.open_url(self.plugin.manifest().get("Website"))
                
                    self.add_result(Result(
                        Title=title,
                        SubTitle=message,
                        JsonRPCAction=json_rpc_action,
                        IcoPath=self.plugin.manifest().get("IcoPath")
                    ))
        except Exception as e:
            self._logger.error(e)
        
        return self.return_results()
