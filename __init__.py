import renpy, sys, os
from modloader.modclass import Mod, loadable_mod
from modloader import modast

@loadable_mod
class AWSWMod(Mod):
    REMY_COMPUTER_SPEECH = "At the press of a button, the screen came to life, accompanied by the whir of the machine. After a few seconds, colorful images appeared on the screen."

    def mod_info(self):
        return ("Grissess' Debug mod.", "v0.1.0", "Grissess")

    def mod_load(self):
        # Add _us_ to the modload list; we need this because the dirname of
        # this mod can change.
        sys.path.append(os.path.dirname(__file__))
        # ... and our submodule:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'unrpyc'))

        modast.call_hook(
                modast.find_say(self.REMY_COMPUTER_SPEECH),
                modast.find_label('eg_remy1_hook'),
        )

        nav_scr = modast.get_slscreen('navigation')
        nav_frame = nav_scr.children[0]  # A little fragile, I know

        nav_item = modast.get_slscreen('eg_pause_menu_item')

        title_scr = modast.get_slscreen('main_menu')

        for child in nav_item.children:
            nav_frame.children.append(child)
            title_scr.children.append(child)

        renpy.config.developer = True

    def mod_complete(self):
        pass
