import logging
import re
from pyflowlauncher import Plugin, Result, Method, api as API
from pyflowlauncher.models.json_rpc import JsonRPCResponse

class Query(Method):
    # Set fixed class attribute
    __name__ = "query"
    
    def __init__(self, plugin: Plugin) -> None:
        super().__init__()
        self.plugin = plugin

    # Dynamically route setting lookups to the plugin settings dict    
    def __getattr__(self, name: str):
        try:
            return self.plugin.settings[name]
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __call__(self, query: str) -> JsonRPCResponse:
        try:
            # Set and convert Log-Level dynamically
            if self.log_level:
                log_level_int = getattr(logging, str(self.log_level).upper(), None)
                if isinstance(log_level_int, int):
                    self.plugin.logger.setLevel(log_level_int)

            icon = self.plugin.manifest.ico_path
            website = self.plugin.manifest.website

            if not query:
                title = "Insert URL"
                message = "e.g. https://example.com"
            
                self.add_result(Result(
                    title=title,
                    subtitle=message,
                    icon=icon
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
                            title = "Please insert a valid URL"
                            message = f"{query}"
                
                            self.add_result(Result(
                                title=title,
                                subtitle=message,
                                icon=icon
                            ))

                    if url_match:
                        remove_paywall_url = self.service + query
                        title = "Open URL"
                        message = f"Open URL in default Browser: {remove_paywall_url}"
                        json_rpc_action = API.open_url(remove_paywall_url)
                    
                        self.add_result(Result(
                            title=title,
                            subtitle=message,
                            json_rpc_action=json_rpc_action,
                            icon=icon
                        ))
                else:
                    title = "ERROR"
                    message = f"Error: No Service for the Paywall removal is set <{self.service}>"
                    json_rpc_action = API.open_url(website)
                
                    self.add_result(Result(
                        title=title,
                        subtitle=message,
                        json_rpc_action=json_rpc_action,
                        icon=icon
                    ))
        except Exception as e:
            self.plugin.logger.error(f"Error executing query: {e}")
        
        return self.return_results()
