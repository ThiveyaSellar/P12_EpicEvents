import pytest
from controller.ClientController import ClientController
from unittest.mock import MagicMock, patch

class TestClientController:

    def test_get_all_clients(self):
        # --- 1. Créer le client factice ---
        mock_client = MagicMock()

        # --- 2. Simuler la session ---
        mock_session = MagicMock()
        mock_session.query().all.return_value = [mock_client]

        # --- 3. Créer un contexte simulé avec les clés .obj attendues ---
        ctx = MagicMock()
        ctx.obj = {
            "session": mock_session,
            "SECRET_KEY": "dummy_secret"  # valeur factice pour le test
        }

        # --- 4. Créer le contrôleur avec ce contexte ---
        controller = ClientController(ctx)

        # --- 5. Simuler la vue show_all_clients ---
        with patch.object(controller.view, "show_all_clients") as mock_show:
            # --- 6. Appeler la fonction testée ---
            result = controller.get_all_clients()

            # --- 7. Vérifications ---
            mock_show.assert_called_with([mock_client])  # la vue a bien été appelée
            assert result == [mock_client]              # la fonction retourne la bonne liste
