style eg_window is window:
    xalign 0.5
    yalign 0.5

style eg_text is text

style eg_button is button:
    hover_sound 'se/sounds/select.ogg'
    activate_sound 'se/sounds/select3.ogg'
    background "#fff2"
    hover_background "#fff4"

style eg_return is eg_button:
    activate_sound 'se/sounds/close.ogg'

style eg_toggle is eg_button:
    selected_background "#4ffa"
    selected_hover_background "#7ffc"

style eg_good_toggle is eg_button:
    background "#0f02"
    hover_background "#0f04"
    selected_background "#0f0"
    selected_hover_background "#4f4"

style eg_bad_toggle is eg_button:
    background "#f002"
    hover_background "#f004"
    selected_background "#f00"
    selected_hover_background "#f44"

style eg_small:
    size 16

style eg_small_text is eg_text:
    take eg_small
style eg_small_toggle is eg_toggle
style eg_small_toggle_text is eg_text:
    take eg_small
style eg_good_small_toggle is eg_good_toggle
style eg_good_small_toggle_text is eg_text:
    take eg_small
style eg_bad_small_toggle is eg_bad_toggle
style eg_bad_small_toggle_text is eg_text:
    take eg_small

label eg_l_root:
    if not persistent.eg_warned:
        play sound "fx/system3.wav"
        s "Heads up! This will void your warranty!"
        s "You can break a {i}ton{/i} of things in the game from here. It's best not to touch anything if you don't understand it!"
        s "Speaking of which, even I don't understand some of it. Don't count on these tools even working..."
        $ persistent.eg_warned = True
    call screen eg_root
    return

screen eg_root:
    style_prefix 'eg'
    window:
        vbox:
            textbutton "Character Status":
                action Function(renpy.call_in_new_context, 'eg_l_charstat')

            textbutton "Play Sequence":
                action Function(renpy.call_in_new_context, 'eg_l_playseq')

            textbutton "Achievements and Milestones":
                action Function(renpy.call_in_new_context, 'eg_l_achievements')

            textbutton "Script Stack":
                action Function(renpy.call_in_new_context, 'eg_l_scriptstack')

            textbutton "Script Jump":
                action Function(renpy.call_in_new_context, 'eg_l_scriptjump')

            textbutton "Variable Editor":
                action Function(renpy.call_in_new_context, 'eg_l_vared')

            textbutton "Python Console":
                action Function(renpy.call_in_new_context, 'eg_l_console')

            textbutton "Developer Mode":
                style "eg_good_toggle"
                selected config.developer
                action ToggleField(config, 'developer')

            textbutton "Return":
                action Return()
                style "eg_return"

label eg_l_charstat:
    call screen eg_charstat
    return

init python:
    import re

    STATUS_CONTINUUM = ['dead', 'abandoned', 'bad', 'none', 'neutral', 'normal', 'good']
    STATUS_COLORS = {
        'dead': '#700',
        'abandoned': '#f00',
        'bad': '#f77',
        'none': '#aaa',
        'neutral': '#fff',
        'normal': '#7f7',
        'good': '#0f0',
    }

    NICKNAMES = {
        'katsu': 'katsuharu',
    }

    ECK_MOD_ENDINGS_SEEN = re.compile('eck(.+)endingseen(.)')

    def alter_status(ch, f):
        varname = ch + 'status'
        value = getattr(store, varname)
        if getattr(store, ch + 'dead', False):
            value = 'dead'
        try:
            index = STATUS_CONTINUUM.index(value)
        except Exception:
            return
        newidx = min((max((0, f(index))), len(STATUS_CONTINUUM) - 1))
        if newidx == index:
            return
        new = STATUS_CONTINUUM[newidx]
        setattr(store, ch + 'dead', new == 'dead')
        setattr(store, varname, 'none' if new == 'dead' else new)

    def improve_status(ch):
        alter_status(ch, lambda x: x+1)

    def diminish_status(ch):
        alter_status(ch, lambda x: x-1)

    def describe_status(ch):
        return 'dead' if getattr(store, ch + 'dead') else getattr(store, ch + 'status')

    CHAR_COLOR_CACHE = {}

    def get_char_color(ch):
        import renpy.character

        ch = ch.lower()
        if ch in CHAR_COLOR_CACHE:
            return CHAR_COLOR_CACHE[ch]

        for vn in dir(store):
            val = getattr(store, vn)
            if isinstance(val, renpy.character.ADVCharacter) and val.name is not None and val.name.lower() in (ch, NICKNAMES.get(ch)):
                CHAR_COLOR_CACHE[ch] = val.who_args['color']
                return CHAR_COLOR_CACHE[ch]

        CHAR_COLOR_CACHE[ch] = '#fff'
        return CHAR_COLOR_CACHE[ch]

    def toggle_eck_modded_ending(char, end):
        var = 'eck%sendingseen%s' % (char, end)
        setattr(persistent, var, end.upper() if getattr(persistent, var) != end.upper() else '...')

style eg_character is eg_text:
    font 'Ardnas.otf'

style eg_status is eg_text:
    xminimum 120

screen eg_charstat:
    default status_chars = set(i[:-6] for i in dir(store) if i.endswith('status') and i not in ('describe_status', 'alter_status', 'diminish_status', 'improve_status'))
    default failing_chars = set(i[:-4] for i in dir(persistent) if i.endswith('fail'))
    default surviving_chars = set(i[:-8] for i in dir(store) if i.endswith('survives'))
    python:
        played_simple = {}
        played_chapters = {}
        for i in dir(persistent):
            nm = None

            if i.endswith('played'):
                nm = i[:-6]
            elif i.startswith('played'):
                nm = i[6:]

            if not nm:
                continue

            if not nm[-1].isdigit():
                played_simple[nm] = i
                continue

            char, chapter = nm[:-1], int(nm[-1])
            played_chapters.setdefault(char, []).append((chapter, i))

        for val in played_chapters.values():
            val.sort(key = lambda pair: pair[0])

        eck_modded_endings = {}
        for i in dir(persistent):
            match = ECK_MOD_ENDINGS_SEEN.match(i)
            if not match:
                continue

            eck_modded_endings.setdefault(match.group(1), []).append(match.group(2))

        for val in eck_modded_endings.values():
            val.sort()

        all_chars = sorted(set(list(played_simple.keys()) + list(played_chapters.keys()) + list(status_chars) + list(failing_chars) + list(surviving_chars)))

    style_prefix 'eg'

    window:
        viewport:
            mousewheel True
            scrollbars "both"

            vbox:
                grid 4 len(all_chars)*2:
                    for char in all_chars:
                        # Row 1

                        text (char.title()):
                            style "eg_character"
                            color get_char_color(char)

                        if char in status_chars:
                            hbox:
                                button: 
                                    add "image/ui/button/left.png"
                                    action Function(diminish_status, char)

                                $ stat = describe_status(char)

                                label stat:
                                    style "eg_status"
                                    text_color STATUS_COLORS[stat]

                                button:
                                    add "image/ui/button/right.png"
                                    action Function(improve_status, char)
                        else:
                            null

                        # Normally, generator expressions are lazy. Normally, that's a good thing. But this generator
                        # captures "char" from the closure above, which causes it to be undefined (as a "global name")
                        # when the condition is actually evaluated. As a hack, this has to be left as a list generator
                        # so as to be evaluated eagerly.
                        if any([isinstance(getattr(persistent, char + kind + 'ending', None), bool) for kind in ('good', 'bad')]):
                            hbox:
                                if isinstance(getattr(persistent, char + 'goodending', None), bool):
                                    textbutton "Good":
                                        style "eg_good_small_toggle"
                                        selected getattr(persistent, char + 'goodending')
                                        action ToggleField(persistent, char + 'goodending')

                                if isinstance(getattr(persistent, char + 'badending', None), bool):
                                    textbutton "Bad":
                                        style "eg_bad_small_toggle"
                                        selected getattr(persistent, char + 'badending')
                                        action ToggleField(persistent, char + 'badending')
                        else:
                            null

                        if char in played_simple:
                            $ var = played_simple[char]

                            textbutton "Played":
                                style "eg_small_toggle"
                                selected getattr(persistent, var)
                                action ToggleField(persistent, var)
                        else:
                            null

                        # Row 2
                        null

                        if char in surviving_chars or char in failing_chars:
                            hbox:
                                if char in surviving_chars:
                                    textbutton "Survives":
                                        style "eg_good_small_toggle"
                                        selected getattr(store, char + 'survives')
                                        action ToggleField(persistent, char + 'survives')

                                if char in failing_chars:
                                    textbutton "Fail":
                                        style "eg_bad_small_toggle"
                                        selected getattr(persistent, char + 'fail')
                                        action ToggleField(persistent, char + 'fail')
                        else:
                            null

                        if char in played_chapters:
                            $ info = played_chapters[char]

                            hbox:
                                for chnum, var in info:
                                    textbutton ("Ch. %d" % (chnum,)):
                                        style "eg_small_toggle"
                                        selected getattr(persistent, var)
                                        action ToggleField(persistent, var)
                        else:
                            null

                        if char in eck_modded_endings:
                            hbox:
                                box_wrap True

                                text "ECK:" style "eg_small_text"

                                $ ends = eck_modded_endings[char]

                                for end in ends:
                                    textbutton (end.upper()):
                                        style "eg_small_toggle"
                                        selected getattr(persistent, 'eck%sendingseen%s' % (char, end)) == end.upper()
                                        action Function(toggle_eck_modded_ending, char, end)
                        else:
                            null

                # Because it's confusing: this is outside the grid, inside the vbox.
                textbutton "Return" action Return() style "eg_return"

label eg_l_playseq:
    call screen eg_playseq
    return

init python:
    CHAPTER_VARS = [2, 3, 4]
    def set_current_chapter(chap):
        for chv in CHAPTER_VARS:
            setattr(store, 'chapter%dunplayed' % (chv,), chap <= chv)

    def guess_current_chapter():
        for chv in CHAPTER_VARS:
            if getattr(store, 'chapter%dunplayed' % (chv,)):
                return chv

        return CHAPTER_VARS[-1] + 1

    def decrement_chapter():
        chap = guess_current_chapter()
        if chap > 1:
            set_current_chapter(chap - 1)

    def increment_chapter():
        chap = guess_current_chapter()
        if chap <= CHAPTER_VARS[-1]:
            set_current_chapter(chap + 1)

    CHAR_VARS = [1, 2, 3, 4, 5]
    def guess_char_seq(char):
        for chv in CHAR_VARS:
            if getattr(store, '%s%dunplayed' % (char, chv)):
                return chv - 1

        return CHAR_VARS[-1]

    def set_char_seq(char, chap):
        for chv in CHAR_VARS:
            played = chv <= chap
            setattr(store, '%s%dplayed' % (char, chv), played)
            setattr(store, '%s%dunplayed' % (char, chv), not played)

    def inc_char_seq(char):
        chap = guess_char_seq(char)
        if chap > CHAR_VARS[0]:
            set_char_seq(char, chap - 1)

    def dec_char_seq(char):
        chap = guess_char_seq(char)
        if chap < CHAR_VARS[-1]:
            set_char_seq(char, chap + 1)

screen eg_playseq:
    default seq_chars = sorted(i[:-7] for i in dir(store) if i.endswith('1played'))

    style_prefix 'eg'

    window:
        viewport:
            mousewheel True
            scrollbars "both"

            vbox:
                text "Note: skipping forward will {i}often{/i} crash the script due to unset variables. Also note that the chapter is only checked when exiting from a character's scene; you may want Script Jump instead.":
                    style "eg_desc"

                grid 2 len(seq_chars)+1:
                    text "Chapter:"

                    hbox:
                        $ cur_chap = guess_current_chapter()

                        button:
                            add "image/ui/button/left.png"
                            action Function(decrement_chapter)
                            sensitive (cur_chap > 1)

                        label ('1 or 2' if cur_chap in (1, 2) else str(cur_chap)):
                            style "eg_status"

                        button:
                            add "image/ui/button/right.png"
                            action Function(increment_chapter)
                            sensitive (cur_chap <= CHAPTER_VARS[-1])

                    for char in seq_chars:
                        text (char.title()):
                            style "eg_character"
                            color get_char_color(char)

                        hbox:
                            $ cur_seq = guess_char_seq(char)

                            button:
                                add "image/ui/button/left.png"
                                action Function(dec_char_seq, char)
                                sensitive (cur_seq > CHAR_VARS[0])

                            label str(cur_seq):
                                style "eg_status"

                            button:
                                add "image/ui/button/right.png"
                                action Function(inc_char_seq, char)
                                sensitive (cur_seq < CHAR_VARS[-1])

                textbutton "Return":
                    action Return()
                    style "eg_return"

init python:
    import collections
    MILESTONES = collections.OrderedDict([
        ('playedadine2', 'Played Adine Chapter 2 (know about Amely)'),
        ('c2pictures', "Seen Remy's pictures in Chapter 2 (asked about Amelia)"),
        ('varasaved', 'Saved Vara after Orange died'),
        ('heardaboutcancer', "Know about Anna's cancer (either way)"),
        ('heardaboutcancerremy', "Know about Anna's cancer from Remy in Chapter 3"),
        ('heardaboutcancerenvelope', "Know about Anna's cancer by reading her mail in Chapter 2"),
        ('orb_taken', "Found Lorem's Ixomen Sphere in the Pavilion"),
        ('base_taken', "Found Lorem's Ixomen Sphere's base in the trash can"),
        ('havetestresults', "Know about Anna's DNA test results (for Maverick)"),
        ('havemap', 'Copied the blueprints for Adine'),
    ])

    ACHIEVEMENTS = collections.OrderedDict([
        ('c1blood', ('Blood donation', 'Give Anna your blood', None)),
        ('c1fish', ('Bravery', 'Order the daily special', 'Ask Adine for it while dining with Reza')),
        ('c1books', ('Bookworm', 'Read a bunch of books', 'Read all the books Remy left in your apartment')),
        ('c1meds', ('Prescription', 'Take a dragon dose of medication', 'Take as many pills as possible from your bathroom')),
        ('c1liquid', ('Daredevil', 'Drink a mysterious liquid', 'Drink the... uh, "white, salty" liquid in the fridge of your apartment')),
        ('c1eggs', ('Ovicide', 'Waste a perfectly good batch of eggs', 'Break all 6 eggs in your apartment')),
        ('c1fruits', ('Fruitarian', 'Learn a lot about fruits', 'Read every fruit pun while raiding your pantry')),
        ('c1decline', ('Nuisance', 'Refuse to help Bryce 99 times', 'Turn down his request for help investigating in Chapter 1')),
        ('c1invhigh', ('Investigator 1', 'Do well on the first investigation', None)),
        ('c1booksort', ('Librarian', "Bring Remy's books into the correct order", 'Inception, First War, Tribe, Second War, Invention, Spark, Third War, Enlightenment')),
        ('c1boredom', ('Patient', 'Wait for Remy until you get bored', 'Wait for Remy three times')),
        ('c1annaanswers', ('Knowledgist', "Answer Anna's questions correctly", 'Haziq Aakil, Three, and None of those')),
        ('c1teetotaler', ('Teetotaler', "Reject Bryce's invitation", "Turn down any of Bryce's requests to drink")),
        ('c1disrobement', ('Disrobement', 'Get Adine to remove her headgear', 'Ask Adine what her biggest regret is')),
        ('c1bastion', ('You are a winner!', 'Beat Sebastian at his own game', 'Win the fixed game of Bastion Breach')),
        ('c2interrogator', ('Interrogator 1', 'Interrogate Damion', 'Ask Damion all questions you can')),
        ('c2bandage', ('Finders, Keepers', 'Acquire the bloody bandage', 'Press both buttons and turn to the left the hatch in north Tatsu Park')),
        ('dirttaken', ('Archeologist', 'Find a handful of dirt', 'Get the dirt from the shrubs in Tatsu Park')),
        ('c2landscape', ('Landscaper', 'Appreciate the landscape', 'Rest on the bench in north Tatsu Park')),
        ('orb_taken', ('Orb Finder', 'Find a mysterious orb', "Find Lorem's Ixomen Sphere by searching the Pavilion at Tatsu Park thrice")),
        ('c2storeaisles', ('Window Shopper', 'Look at everything the store has to offer', "Thoroughly search Zhong's store")),
        ('c2investigation', ('Investigator 2', 'Do well on the second investigation', None)),
        ('c2pictures', ('Memories', "Look at Remy's pictures", "Spend all three waiting rounds at Remy's house looking at his pictures")),
        ('heardaboutcancerenvelope', ('Snoop', "Look at Anna's envelope", "Discover Anna's cancer by peeking at her mail in Chapter 2")),
        ('c2legs', ('Leg Stretcher', 'Stretch your legs', 'Stretch your legs while waiting for Bryce in Chapter 2')),
        ('c2eau', ('Eau de Dragon', "Examine Bryce's blanket", 'Examine the blanket while waiting for Bryce in Chapter 2')),
        ('c2magazine', ('Research Material', "Look at Bryce's magazine", "Read Bryce's magazine while waiting for him in Chapter 2")),
        ('c2music', ('Audiophile', 'Listen to a bunch of music', "Listen (you need not finish) to each of Zhong's music selections")),
        ('playedemera', ('The Politician', 'Meet with Emera', 'Have a Remy ending, meet Remy at least once, and make fun of him in front of Emera at Tatsu Park')),
        ('havemapfirst', ('Cartographer', 'Acquire a map', 'Copy the blueprints in the police station')),
        ('base_taken', ('Base Finder', 'Find a mysterious base', "Find Lorem's Ixomen Sphere's Base in the trash at the police station")),
        ('c3prank', ('Prankster', 'Play a prank on Bryce', 'Prank Bryce at the police station')),
        ('c3helpedkatsu', ('Altruist', 'Help Katsuharu', "Fix Katsuharu's cart on the way to the police station")),
        ('c3interrogator', ('Interrogator 2', 'Interrogate Anna', "Ask Anna every question about Damion's death")),
        ('varasaved', ('Stalker', 'Follow Vara', "Save Vara after her mother dies by chasing her from Zhong's store")),
        ('c3reckless', ('Reckless', 'Go to the portal', "Ignore the Administrator's request to not go near the portal (and fail anyway)")),
        ('c3investigator', ('Investigator 3', 'Do well on the third investigation', None)),
        ('c3flawless', ('Flawless Run', 'Do well in all investigations in a single playthrough', None)),
        ('seashells', ('Souvenir', 'Keep the seashells', "Tell Adine that you're keeping the seashells as souvenirs")),
        ('playedkatsu', ('The Artisan', 'Meet with Katsuharu', 'Meet him after assisting him on your way to the police station')),
        ('c4eggs', ('In Loco Parentis', 'Return the eggs to the hatchery', None)),
        ('ixomenassembled', ('Sphere Builder', 'Assemble the sphere', 'Bring both the base and orb to Lorem')),
        ('playedkevin', ('The Student', 'Meet with Kevin', 'Meet him after encountering him on the way to the hatchery')),
        ('lazy', ('Lazy', 'Decide not to meet anyone or investigate 10 times', None)),
        ('skip', ('Fast Forward', 'Skip ahead 10 times', None)),
        ('popular', ('Popular', 'Have two messages waiting for you at the same time', None)),
        ('c3pointless', ('Utterly Pointless Achievement', 'Do a thing', "Have seen five different endings by the beginning of Chapter 4's investigation")),
        ('izumimask', ('Unmasking', 'See what lies beneath the mask', 'View any ending where Izumi reveals herself or is shot')),
        ('firstending', ('It Begins', 'See your first ending', None)),
        ('neutralending', ('Detonation', 'See the neutral ending', None)),
        ('remybadending', ('Alone', "See Remy's bad ending", 'Wherein Remy alone survives the impactor by returning to your desolate world')),
        ('remygoodending', ('Casualties of War', "See Remy's good ending", 'Wherein Reza kills Vara, and the diplomacy falls apart')),
        ('annabadending', ('Sacrifice', "See Anna's bad ending", 'Wherein Anna sacrifices herself to be free from her suffering and save you')),
        ('annagoodending', ('Tragic Hero', "See Anna's good ending", 'Wherein Anna, exonerated, dies of cancer')),
        ('lorembadending', ('Remember', "See Lorem's bad ending", 'Wherein Lorem is killed in the generator explosion, Reza survives, but the impact occurs')),
        ('loremgoodending', ('The Plan', "See Lorem's good ending", 'Wherein you teleport Reza to Izumi on the first day, and bury him')),
        ('brycebadending', ('Catastrophe', "See Bryce's bad ending", 'Wherein Bryce dies from the generator explosion and Maverick nearly kills you for it')),
        ('brycegoodending', ('Murderer', "See Bryce's good ending", 'Wherein you murder Maverick for killing Izumi in the heat of the moment')),
        ('adinebadending', ('Getaway', "See Adine's bad ending", 'Wherein Reza gets away with the generator and cuts the portal')),
        ('adinegoodending', ('Decisions', "See Adine's good ending", 'Wherein you must decide if you, or your double playing the Administrator, must go back to find the best ending for both worlds')),
        ('evilending', ('Betrayal', 'See the evil ending', 'Wherein you kill Reza, steal the generator to humanity, and leave the dragons to extinction')),
        ('optimist', ('Optimist', 'See your first good ending', None)),
        ('trueending', ('Hope', 'See the true ending', 'Wherein Izumi has her soliloquy and dies in peace')),
    ])

    def recompute_achievements():
        persistent.achievements = sum(1 if getattr(persistent, name) else 0 for name in ACHIEVEMENTS.keys())

label eg_l_achievements:
    call screen eg_achievements
    return

style eg_milestone is eg_small_toggle:
    bold True
style eg_milestone_text is eg_small_toggle_text
style eg_achievement is eg_milestone
style eg_achievement_text is eg_milestone_text

style eg_desc is eg_text:
    size 16
    color "#777"

style eg_ingame_desc is eg_desc:
    color "#fff"

screen eg_achievements:
    style_prefix 'eg'
    window:
        viewport:
            mousewheel True
            scrollbars "both"

            vbox:
                grid 2 len(MILESTONES):
                    spacing 16

                    for ms, desc in MILESTONES.items():
                        textbutton ms:
                            style "eg_milestone"
                            selected getattr(persistent, ms)
                            action ToggleField(persistent, ms)
                            xmaximum 400

                        text desc style "eg_desc" xmaximum 400

                null height 48

                text "Note: it is not yet possible to automatically enumerate mod achievements.":
                    style "eg_desc"

                grid 3 len(ACHIEVEMENTS):
                    spacing 16

                    for ach, parts in ACHIEVEMENTS.items():
                        python:
                            title, igd, exd = parts
                            if exd is None:
                                exd = ''

                        textbutton title:
                            style "eg_achievement"
                            selected getattr(persistent, ach)
                            action [ToggleField(persistent, ach), Function(recompute_achievements)]
                            xmaximum 400

                        text igd style "eg_ingame_desc" xmaximum 400

                        text exd style "eg_desc" xmaximum 400

                text ("Achievement Count: %d / %d" % (persistent.achievements, len(ACHIEVEMENTS)))

                null height 48

                textbutton "Return":
                    action Return()
                    style "eg_return"

label eg_l_scriptstack:
    call screen eg_scriptstack
    return  # This could ROP!

init python:
    def pop_from_return_stack(cx):
        cx.set_return_stack(cx.get_return_stack()[:-1])  # Slicing shallow-copies anyway

style eg_stack_entry is eg_button
style eg_nonlabel_stack_entry is eg_stack_entry:
    background "#f002"
    hover_background "#f004"

style eg_context is eg_toggle

style eg_index is eg_text:
    color "#077"
    italic True

style eg_return_rop is eg_return:
    background "#0f02"
    hover_background "#0f04"

screen eg_scriptstack:
    default cxidx = len(renpy.game.contexts) - 1

    style_prefix 'eg'
    window:
        viewport:
            mousewheel True
            scrollbars "both"

            vbox:
                hbox:
                    text "Context:"

                    null width 48

                    for i in range(len(renpy.game.contexts)):
                        textbutton str(i):
                            style "eg_context"
                            action SetScreenVariable('cxidx', i)
                            selected i == cxidx

                $ cx = renpy.game.context(cxidx)
                $ rs = cx.get_return_stack()
                
                text "Bottom" style "eg_index"


                for idx, label in enumerate(rs):
                    hbox:
                        text str(idx):
                            style "eg_index"

                        null width 16

                        textbutton repr(label):
                            style ("eg_nonlabel_stack_entry" if isinstance(label, tuple) else "eg_stack_entry")
                            action Function(renpy.call_in_new_context, 'eg_l_replace_stack', cx, idx)

                text "Top" style "eg_index"

                null height 48

                if cxidx == len(renpy.game.contexts) - 1:
                    text "You are in the current context; if the stack is not empty, returning from here will ROP (jump) into the top of the stack as it is right now.":
                        italic True
                        color "#070"

                    null height 48

                if cxidx == 0:
                    text "You are in the top context; this is usually the actual game state. Be careful!":
                        italic True
                        color "#700"

                hbox:
                    textbutton "Push":
                        # It's fine to create a new context (and thus a new return stack here); since it
                        # is only created as a side-effect of this function, it cannot be referenced before
                        # the action is actually invoked.
                        action Function(renpy.call_in_new_context, 'eg_l_push_stack', cx)

                    textbutton "Pop":
                        action Function(pop_from_return_stack, cx)

                    textbutton "Return":
                        action Return()
                        style ("eg_return_rop" if cxidx == len(renpy.game.contexts) - 1 and bool(cx.get_return_stack) else "eg_return")

label eg_l_replace_stack(cx, idx):
    call screen eg_replace_stack(cx, idx)

    python:
        if _return is not None:
            stack = list(cx.get_return_stack())
            stack[idx] = _return.encode()  # This needs to be str, not unicode
            cx.set_return_stack(stack)

    # Fortunately, this can't ROP--a new context was created for this call.
    return

style eg_jumplabel is eg_button
style eg_nonlabel_return is eg_return:
    background "#f002"
    hover_background "#f004"

screen eg_replace_stack(cx, idx):
    default labels = sorted(renpy.get_all_labels())
    default currently = cx.get_return_stack()[idx]

    style_prefix 'eg'

    window:
        viewport:
            mousewheel True
            scrollbars "both"

            vbox:
                hbox:
                    text "Current entry:"

                    textbutton repr(currently):
                        action Return()
                        style ("eg_nonlabel_return" if isinstance(currently, tuple) else "eg_return")

                null height 48

                # FIXME: this list is huge and causes performance problems--optimize?
                for label in labels:
                    textbutton label:
                        style "eg_jumplabel"
                        action Return(label)

                null height 48

                textbutton "Cancel":
                    style "eg_return"
                    action Return()

label eg_l_push_stack(cx):
    call screen eg_push_stack(cx)

    python:
        if _return is not None:
            stack = list(cx.get_return_stack())
            stack.append(_return.encode())  # see eg_l_replace_stack
            cx.set_return_stack(stack)

    # See the admonition in eg_l_replace_stack. 
    return

screen eg_push_stack(cx):
    default labels = sorted(renpy.get_all_labels())

    style_prefix 'eg'

    window:
        viewport:
            mousewheel True
            scrollbars "both"

            vbox:
                for label in labels:
                    textbutton label:
                        style "eg_jumplabel"
                        action Return(label)

                null height 48

                textbutton "Cancel":
                    style "eg_return"
                    action Return()

label eg_l_scriptjump:
    call screen eg_scriptjump
    return  # Only if the user cancels

init python:
    def top_context_goto(label):
        raise renpy.game.RestartTopContext(label)

screen eg_scriptjump:
    default labels = sorted(renpy.get_all_labels())

    style_prefix 'eg'

    window:
        viewport:
            mousewheel True
            scrollbars "both"

            vbox:
                text "Note: This is somewhat unkind to both the script and Ren'Py itself. Beware that this function can fail in exciting ways, and also that no attempt is (yet) made to 'warp' to the line (e.g., change music or scenery).":
                    color "#700"

                null height 48

                for label in labels:
                    textbutton label:
                        action Function(top_context_goto, label)

                null height 48

                textbutton "Return":
                    action Return()
                    style "eg_return"

init python:
    import sys
    import cStringIO
    from grissess_debug import code

    class RenpyConsole(code.InteractiveInterpreter):
        STYLE_TAGS = {
            'output': None,
            'error': ('{color=#f00}', '{/color}'),
            'input': ('{color=#070}', '{/color}'),
            'prompt': ('{color=#007}', '{/color}'),
        }

        INSTANCE = None

        @staticmethod
        def escape_text(s):
            return s.replace('[', '[[').replace('{', '{{')

        def __init__(self, *args, **kwargs):
            super(RenpyConsole, self).__init__(*args, **kwargs)

            if not hasattr(sys, 'ps1'):
                sys.ps1 = '>>> '
            if not hasattr(sys, 'ps2'):
                sys.ps2 = '... '

            self.buffer = ''
            self.style = 'output'
            self.prompt = sys.ps1
            self.prev_input = ''
            self.input = ''

            self.write('Python %s on %s\n' % (sys.version, sys.platform))

        def runsource(self, src, fn='<input>', sym='single'):
            self.write(self.prompt, style = 'prompt')
            self.write(src + '\n', style = 'input')

            more = super(RenpyConsole, self).runsource(self.prev_input + src, fn, sym)
            if more:
                self.prev_input += src + '\n'
            else:
                self.prev_input = ''

            self.prompt = sys.ps2 if more else sys.ps1

        def runcode(self, co):
            out = cStringIO.StringIO()
            old_stdout = sys.stdout
            sys.stdout = out
            super(RenpyConsole, self).runcode(co)
            sys.stdout = old_stdout
            self.write(out.getvalue(), 'output')

        def write(self, v, style=None):
            if style is None:
                style = self.style

            tags = self.STYLE_TAGS.get(style, None)
            if tags is None:
                tags = ('', '')

            self.buffer += tags[0] + self.escape_text(v) + tags[1]

        def showsyntaxerror(self, fn=None):
            self.style = 'error'
            super(RenpyConsole, self).showsyntaxerror(fn)
            self.style = 'output'

        def showtraceback(self):
            self.style = 'error'
            super(RenpyConsole, self).showtraceback()
            self.style = 'output'

label eg_l_console:
    python:
        RenpyConsole.INSTANCE = RenpyConsole(locals())
        while True:
            _return = renpy.call_screen('eg_console')
            print('console:', repr(_return))
            if not isinstance(_return, basestring):
                break
            RenpyConsole.INSTANCE.runsource(_return)
            RenpyConsole.INSTANCE.input = ''
    return

style eg_console is eg_text
style eg_prompt is eg_console:
    color "#007"
style eg_input is eg_console:
    color "#070"

screen eg_console:
    window:
        vbox:
            viewport:
                mousewheel True
                scrollbars "vertical"
                xfill True
                yminimum 800

                text RenpyConsole.INSTANCE.buffer:
                    style "eg_console"

            hbox:
                text RenpyConsole.INSTANCE.prompt:
                    style "eg_prompt"

                input:
                    xminimum 800
                    value FieldInputValue(RenpyConsole.INSTANCE, 'input', returnable = True)

                textbutton "Submit":
                    action Return(RenpyConsole.INSTANCE.input)

                textbutton "Return":
                    style "eg_return"
                    action Return()