import logging

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.enums import (
    TipoNegocio,
    OrigenProspecto,
)
from app.integrations.google_places_service import GooglePlacesService
from app.services.prospecto_service import ProspectoService
from app.schemas.prospecto import ProspectoCreate
from app.schemas.sourcing import (
    SourcingBuscarRequest,
    SourcingResultado,
    SourcingBuscarResponse,
)
from app.utils.telefono import (
    normalizar_telefono,
    TelefonoFijoError,
)

logger = logging.getLogger(__name__)

TERMINOS_BUSQUEDA = {

    TipoNegocio.PIZZERIA: "pizzerías",

    TipoNegocio.PANADERIA: "panaderías",

    TipoNegocio.RESTAURANTE: "restaurantes",

    TipoNegocio.CAFETERIA: "cafeterías",

    TipoNegocio.HAMBURGUESERIA: "hamburgueserías",

}


class SourcingService:

    def __init__(self, db: Session):

        self.db = db

        self.places_service = GooglePlacesService()

        self.prospecto_service = ProspectoService(db)

    def buscar(
        self,
        data: SourcingBuscarRequest
    ) -> SourcingBuscarResponse:

        termino = TERMINOS_BUSQUEDA.get(
            data.tipo_negocio
        )

        if termino is None:

            raise ValueError(
                f"El tipo de negocio '{data.tipo_negocio.value}' "
                f"no tiene un término de búsqueda definido para "
                f"sourcing. Usa uno de: "
                f"{', '.join(t.value for t in TERMINOS_BUSQUEDA)}."
            )

        query = f"{termino} en {data.zona}"

        places = self.places_service.buscar_texto(
            query,
            data.max_resultados
        )

        resultados = []

        importados = 0

        duplicados = 0

        descartados_sin_telefono = 0

        descartados_telefono_invalido = 0

        descartados_telefono_fijo = 0

        for place in places:

            resultado, tipo_resultado = self._procesar_place(
                place,
                data
            )

            resultados.append(resultado)

            if tipo_resultado == "importado":
                importados += 1

            elif tipo_resultado in (
                "duplicado",
                "duplicado_telefono"
            ):
                duplicados += 1

            elif tipo_resultado == "descartado_sin_telefono":
                descartados_sin_telefono += 1

            elif tipo_resultado == "descartado_telefono_invalido":
                descartados_telefono_invalido += 1

            elif tipo_resultado == "descartado_telefono_fijo":
                descartados_telefono_fijo += 1

        return SourcingBuscarResponse(

            query=query,

            dry_run=data.dry_run,

            total_encontrados=len(places),

            importados=importados,

            duplicados=duplicados,

            descartados_sin_telefono=descartados_sin_telefono,

            descartados_telefono_invalido=descartados_telefono_invalido,

            descartados_telefono_fijo=descartados_telefono_fijo,

            resultados=resultados
        )

    def _procesar_place(
        self,
        place: dict,
        data: SourcingBuscarRequest
    ):

        google_place_id = place.get("id")

        nombre_empresa = place.get(
            "displayName",
            {}
        ).get("text")

        direccion = place.get(
            "formattedAddress"
        )

        telefono_google = place.get(
            "internationalPhoneNumber"
        )

        if not telefono_google:

            return (

                SourcingResultado(

                    google_place_id=google_place_id,

                    nombre_empresa=nombre_empresa,

                    telefono=None,

                    direccion=direccion,

                    estado_resultado="descartado_sin_telefono"

                ),

                "descartado_sin_telefono"

            )

        try:

            telefono = normalizar_telefono(
                telefono_google
            )

        except TelefonoFijoError as e:

            logger.info(
                f"Teléfono fijo descartado para "
                f"'{nombre_empresa}' (place_id={google_place_id}): "
                f"{e}"
            )

            return (

                SourcingResultado(

                    google_place_id=google_place_id,

                    nombre_empresa=nombre_empresa,

                    telefono=telefono_google,

                    direccion=direccion,

                    estado_resultado="descartado_telefono_fijo"

                ),

                "descartado_telefono_fijo"

            )

        except ValueError as e:

            logger.warning(
                f"Teléfono de Google no válido para "
                f"'{nombre_empresa}' (place_id={google_place_id}): "
                f"{e}"
            )

            return (

                SourcingResultado(

                    google_place_id=google_place_id,

                    nombre_empresa=nombre_empresa,

                    telefono=telefono_google,

                    direccion=direccion,

                    estado_resultado="descartado_telefono_invalido"

                ),

                "descartado_telefono_invalido"

            )

        existente = (
            self.prospecto_service
            .buscar_por_google_place_id(
                google_place_id
            )
        )

        if existente is not None:

            return (

                SourcingResultado(

                    google_place_id=google_place_id,

                    nombre_empresa=nombre_empresa,

                    telefono=telefono,

                    direccion=direccion,

                    estado_resultado="duplicado"

                ),

                "duplicado"

            )

        if data.dry_run:

            return (

                SourcingResultado(

                    google_place_id=google_place_id,

                    nombre_empresa=nombre_empresa,

                    telefono=telefono,

                    direccion=direccion,

                    estado_resultado="pendiente_importar"

                ),

                "pendiente_importar"

            )

        try:

            self.prospecto_service.crear_prospecto(

                ProspectoCreate(

                    nombre_empresa=nombre_empresa,

                    telefono=telefono,

                    ciudad=data.zona,

                    direccion=direccion,

                    tipo_negocio=data.tipo_negocio,

                    origen=OrigenProspecto.GOOGLE_MAPS,

                    google_place_id=google_place_id

                )

            )

        except IntegrityError:

            self.db.rollback()

            logger.warning(
                f"No se pudo importar '{nombre_empresa}' "
                f"(place_id={google_place_id}): ya existe un "
                f"prospecto con el mismo teléfono."
            )

            return (

                SourcingResultado(

                    google_place_id=google_place_id,

                    nombre_empresa=nombre_empresa,

                    telefono=telefono,

                    direccion=direccion,

                    estado_resultado="duplicado_telefono"

                ),

                "duplicado_telefono"

            )

        return (

            SourcingResultado(

                google_place_id=google_place_id,

                nombre_empresa=nombre_empresa,

                telefono=telefono,

                direccion=direccion,

                estado_resultado="importado"

            ),

            "importado"

        )
