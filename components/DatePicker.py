from dash import dcc

def create_date_picker(
    id, 
    placeholder="Select a date", 
    display_format="DD/MM/YYYY"
):
    """
    A reusable DatePicker component.
    
    Args:
        id (str): The ID of the DatePicker component
        placeholder (str): Placeholder text to display when no date is selected
        display_format (str): Format to display the selected date
    
    Returns:
        dash component: A styled DatePicker component
    """

    return dcc.DatePickerSingle(
        id=id,
        placeholder=placeholder,
        display_format=display_format,
        style={
            'zIndex': 1000,  # Ensure dropdown appears above other elements
            'width': '100%',
            'marginBottom': '10px'
        },
        className='date-picker'
    )
