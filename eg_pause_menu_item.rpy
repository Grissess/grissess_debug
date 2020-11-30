# Hooked into the "navigation menu" by __init__
screen eg_pause_menu_item:
    textbutton "Debug":
        text_font "Ardnas.otf"
        align (0.5, 0.87)
        action Function(renpy.call_in_new_context, 'eg_l_root')
