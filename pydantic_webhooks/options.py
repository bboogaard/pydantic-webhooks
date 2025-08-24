import inspect


def create_config(config_class):
    attributes = inspect.getmembers(config_class, lambda a:not(inspect.isroutine(a)))
    attrs = {a[0]: a[1] for a in attributes if not(a[0].startswith('__') and a[0].endswith('__'))}
    return type('ConfigObject', (config_class,), attrs)()
