# Permissions par équipe
all_permissions = [
    "list-clients",
    "list-contracts",
    "list-events",
    "logout",
    "exit"
]

SALES_PERMISSIONS = all_permissions + \
                    [
                        "create-my-client",
                        "update-my-client",
                        "list-filtered-contracts",
                        "update-my-contracts",
                        "create-event-for-my-client",
                    ]

SUPPORT_PERMISSIONS = all_permissions + \
                      [
                          "update-my-event",
                          "list-my-events"
                      ]

MANAGEMENT_PERMISSIONS = all_permissions + \
                         [
                             "create-co-worker",
                             "update-co-worker",
                             "delete-co-worker",
                             "create-contract",
                             "update-contract",
                             "list-events-without-support",
                             "list-events-without-contract",
                             "add-support-collab-to-event"
                         ]

PERMISSIONS = {
    "Commercial": SALES_PERMISSIONS,
    "Support": SUPPORT_PERMISSIONS,
    "Gestion": MANAGEMENT_PERMISSIONS
}

def is_authorized(team, command, permissions):
    return command in permissions.get(team, [])