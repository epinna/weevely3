from prompt_toolkit.styles import Style

default_style = Style.from_dict({
    'bottom-toolbar': 'noreverse',
    'bottom-toolbar.text': 'bg:#ff0000',
    'rprompt': 'bg:#ff0066 #000000',
    'username': '#a6e22e bold',
    'username.root': '#ff4689 underline',
    'at': '#ae81ff',
    'colon': '#ae81ff',
    'pound': '#959077',
    'host': '#66d9ef',
    'path': 'ansicyan',
    'mode': '#ff0000',
    'gutter': '#999999',
    'label': '#00aa00 bold',
    'value': '#33ff66',

    'warning': '#ff4689',
    'danger': '#ed007e',

    'completion-menu': 'bg:#96d0f7 #000000',
    'completion-menu.completion.current': 'bg:#0077ff #000000',
    'completion-menu.completion.alias': 'bg:#1a9cf2',
})