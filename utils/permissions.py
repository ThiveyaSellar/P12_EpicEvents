# Permissions par équipe
all_permissions = [
    "show-clients",
    "show-contracts",
    "show-events",
    "logout",
    "exit"
]

sales_permissions = all_permissions + \
                    [
                        "create-client",
                        "update-client",
                        "show-filtered-contracts",
                        "update-my-contracts",
                        "create-event-for-my-client"
                    ]

support_permissions = all_permissions + \
                      [
                          "update-support-event",
                          "show-support-events"
                          # ...
                      ]

management_permissions = all_permissions + \
                         [
                             "create-co-worker",
                             "update-co-worker",
                             "delete-co-worker",
                             "create-contract",
                             "update-contract",
                             "show-filtered-events"
                             "update-event"
                             # ...
                         ]

PERMISSIONS = {
    "Commercial": sales_permissions,
    "Support": support_permissions,
    "Gestion": management_permissions
}

def is_authorized(team, command, permissions):
    return command in permissions.get(team, [])