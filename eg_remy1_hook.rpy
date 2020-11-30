label eg_remy1_hook:
    m "It looks like a boring spreadsheet is open, but there is another minimized application with a colorful icon. Could it be a game?"

    menu:
        "Look at the spreadsheet.":
            stop music fadeout 1.0
            m "Upon closer inspection..."
            call eg_l_root
            with dissolve
            m "...Well, that was interesting."
            play music "mx/fireplace.ogg" fadein 1.0

            # Fix up the return stack a little bit, since we were _called_
            # Effectively, we're "returning" to a different label
            $ renpy.pop_call()
            jump remyoffmenu

        "Look at the other application.":
            # And let the games begin... Sorry, Remy...
            return
