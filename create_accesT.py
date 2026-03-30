import time, os
import requests
from dotenv import load_dotenv

load_dotenv()

refresh_token = os.getenv("EMAIL_REFRESH_TOKEN") or os.getenv("REFRESH_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
SECRET = os.getenv("SECRET")


class invalid_grant(Exception):
    def __init__(self):
        super().__init__(
            "El refresh token  ha caducado o es inválido. Se requiere un nuevo refresh token."
        )


class accessTokenGen:
    def __init__(self, refresh_token: str | None = None):
        load_dotenv()
        self.refresh_token = refresh_token or (
            os.getenv("EMAIL_REFRESH_TOKEN") or os.getenv("REFRESH_TOKEN")
        )
        if not self.refresh_token:
            raise ValueError("No se encontro refresh_token en las variables de entorno")
        self.get_access(init=True)

    def get_access(self, init: bool = False) -> str:
        current_time = time.time()

        if init or current_time >= self.expiration_time:
            # Token expirado o primera ejecucion. Obtener uno nuevo

            response = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": CLIENT_ID,
                    "client_secret": SECRET,
                    "refresh_token": self.refresh_token,
                    "grant_type": "refresh_token",
                },
            )

            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.expiration_time = current_time + data["expires_in"] - 60

                return self.access_token

            elif response.json().get("error") == "invalid_grant":
                raise invalid_grant
            else:
                raise Exception(
                    f"Error al obtener access token: {response.status_code} - {response.text}"
                )

        else:
            return self.access_token


if __name__ == "__main__":
    try:
        token_manager = accessTokenGen()
        print("Access Token:", token_manager.get_access())
    except Exception as e:
        print("Error al obtener el access token:", str(e))
