# Permissions par équipe
all_permissions = [
    "list-clients",
    "list-contracts",
    "list-events",
    "logout",
    "exit"
]

sales_permissions = all_permissions + \
                    [
                        "create-client",
                        "update-client",
                        "list-filtered-contracts",
                        "update-my-contracts",
                        "create-event-for-my-client",
                    ]

support_permissions = all_permissions + \
                      [
                          "update-my-event",
                          "list-my-events"
                      ]

management_permissions = all_permissions + \
                         [
                             "create-co-worker",
                             "update-co-worker",
                             "delete-co-worker",
                             "create-contract",
                             "update-contract",
                         ]

PERMISSIONS = {
    "Commercial": sales_permissions,
    "Support": support_permissions,
    "Gestion": management_permissions
}

def is_authorized(team, command, permissions):
    return command in permissions.get(team, [])