import dash_bootstrap_components as dbc
from dash import html

def create_tabs(
    tabs_config=None,
    active_tab=None,
    id=None,
    class_name=None,
    style=None
):
    """
    Create a customizable tabs component.
    
    Parameters:
    -----------
    tabs_config : list of dict
        List of dictionaries with tab configurations. Each dictionary should have:
        - content: The content to display in the tab
        - id: Unique identifier for the tab (optional)
        - label: Display label for the tab
        - disabled: Boolean to disable the tab (optional)
    active_tab : str
        ID of the tab that should be active by default
    id : str
        ID for the entire tabs component
    class_name : str
        CSS class name for the tabs component
    style : dict
        Additional CSS styles for the tabs component
    
    Returns:
    --------
    dash_bootstrap_components.Tabs
        A Tabs component with the configured tabs
    """
    tabs = []
    for tab in tabs_config:
        tab_kwargs = {
            "label": tab.get("label", ""),
            "tab_id": tab.get("id", None)
        }

        if "disabled" in tab:
            tab_kwargs["disabled"] = tab["disabled"]

        tabs.append(dbc.Tab(tab.get("content", ""), **tab_kwargs))

    tabs_kwargs = {}
    if active_tab:
        tabs_kwargs["active_tab"] = active_tab
    if id:
        tabs_kwargs["id"] = id
    if class_name:
        tabs_kwargs["className"] = class_name
    if style:
        tabs_kwargs["style"] = style

    return dbc.Tabs(tabs, **tabs_kwargs)
