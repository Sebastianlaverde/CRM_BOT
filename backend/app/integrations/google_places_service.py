import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

TEXT_SEARCH_URL = (
    "https://places.googleapis.com/v1/places:searchText"
)

FIELD_MASK = (
    "places.id,"
    "places.displayName,"
    "places.formattedAddress,"
    "places.internationalPhoneNumber"
)


class GooglePlacesService:

    def buscar_texto(
        self,
        query: str,
        max_resultados: int
    ) -> list[dict]:

        if not settings.GOOGLE_PLACES_API_KEY:

            raise ValueError(
                "GOOGLE_PLACES_API_KEY no está configurada."
            )

        try:

            response = httpx.post(

                TEXT_SEARCH_URL,

                headers={

                    "X-Goog-Api-Key": (
                        settings.GOOGLE_PLACES_API_KEY
                    ),

                    "X-Goog-FieldMask": FIELD_MASK,

                    "Content-Type": "application/json"

                },

                json={

                    "textQuery": query,

                    "maxResultCount": max_resultados

                },

                timeout=15
            )

            response.raise_for_status()

        except httpx.HTTPStatusError as e:

            logger.exception(
                f"Error de Google Places API: {e.response.text}"
            )

            raise ValueError(
                f"Google Places API respondió con error "
                f"{e.response.status_code}: {e.response.text}"
            )

        except httpx.HTTPError as e:

            logger.exception(
                f"Error de red llamando a Google Places API: {e}"
            )

            raise ValueError(
                f"No fue posible contactar a Google Places API: {e}"
            )

        return response.json().get(
            "places",
            []
        )
