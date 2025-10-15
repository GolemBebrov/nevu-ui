import nevu_ui as ui

def test_typehints():
    basic_kwargs = {
        "size": [50,50],
        "style": ui.default_style(),
    }
    
    basic_widget = ui.Widget(**basic_kwargs)
    
    ui.LayoutType(**basic_kwargs, content = [basic_widget]) 
    
    ui.Grid(**basic_kwargs, content = {(1,1): basic_widget})
    
    ui.Row(**basic_kwargs, content = {1: basic_widget})
    
    ui.Column(**basic_kwargs, content= {1: basic_widget})
    
    ui.StackRow(**basic_kwargs, content = [(ui.Align.CENTER, basic_widget)])
    
    ui.StackColumn(**basic_kwargs, content = [(ui.Align.CENTER, basic_widget)])
    
    ui.Scrollable(**basic_kwargs, content = [(ui.Align.CENTER, basic_widget)])
    
    ui.Pages(**basic_kwargs, content = [basic_widget])
    