from config import system_variables

def system_variables_view(request):
    return {attr: getattr(system_variables, attr) for attr in dir(system_variables) if not attr.startswith("__")}

