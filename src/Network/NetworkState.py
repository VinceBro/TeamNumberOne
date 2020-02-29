

class CommandNetwork:
    # COMMAND FROM CLIENT TO SERVER
    CMD_WATCH_PARTY = 'cmd_watch'
    CMD_UPDATE_STATUS = 'cmd_update'
    CMD_TRY_CONNEXION = 'cmd_connexion'
    CMD_GET_PARTIES = 'cmd_get'
    CMD_CREATE_PARTY = 'cmd_create'
    CMD_JOIN_PARTY = 'cmd_join'

    # SUB-CMD UPDATE STATUS
    GAME_INFO = 'game_info'
    MOBILE_OBJECTS_INFO = 'mob_info'
    PLAYER_INFO = 'player_info'

    # COMMAND FROM SERVER
    CMD_CONNEXION_OK = 'cmd_connexion_ok'
    CMD_CONNEXION_REFUSED = 'cmd_connexion_refused'
    CMD_CREATE_PARTY_OK = 'cmd_create_party_ok'
    CMD_CREATE_PARTY_REFUSED = 'cmd_create_party_refused'
    CMD_JOIN_PARTY_OK = 'cmd_join_party_ok'
    CMD_JOIN_PARTY_REFUSED = 'cmd_join_party_refused'


class PlayerMode:
    MODE_PING_PONG = 'mode_playing'
    MODE_WAITING = 'mode_waiting'
    MODE_SENDER = 'mode_mwenu'
    MODE_QUIT = 'mode_quit'
