import configparser

import pushover

config = configparser.ConfigParser()
config.read('/config/config.ini')

class Client:
    def __init__(self, *args, **kwargs):
        self.wrapped_class = pushover.Client(*args, **kwargs)

    def __getattr__(self, attr):
        orig_attr = self.wrapped_class.__getattribute__(attr)
        if callable(orig_attr):
            def hooked(*args, **kwargs):
                result = orig_attr(*args, **kwargs)
                # prevent wrapped_class from becoming unwrapped
                if result == self.wrapped_class:
                    return self
                return result

            return hooked
        else:
            return orig_attr

    def send_message(self, message, *args, **kwargs):
        if config['pushover'].getboolean('debug'):
            print(message)
        else:
            self.wrapped_class.send_message(message, *args, **kwargs)
