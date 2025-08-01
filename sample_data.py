#!/usr/bin/env python3
"""
Datos de muestra para la aplicación de Costumbres Mercantiles
"""

SAMPLE_DATA = [
    {
        "ciudad": "Bogotá",
        "tipo": "Comercial",
        "contenido": "En las transacciones comerciales de Bogotá, es costumbre que los pagos se realicen dentro de los primeros 5 días del mes siguiente a la entrega de la mercancía."
    },
    {
        "ciudad": "Medellín",
        "tipo": "Bancario",
        "contenido": "En el sector bancario de Medellín es práctica común que los cheques de gerencia se emitan con validez de 90 días calendario."
    },
    {
        "ciudad": "Cali",
        "tipo": "Comercial",
        "contenido": "En Cali, las empresas del sector azucarero acostumbran realizar sus pagos los días 15 y 30 de cada mes."
    },
    {
        "ciudad": "Barranquilla",
        "tipo": "Portuario",
        "contenido": "En el puerto de Barranquilla es costumbre que los fletes marítimos se liquiden en dólares americanos al cambio del día de zarpe de la nave."
    },
    {
        "ciudad": "Cartagena",
        "tipo": "Turístico",
        "contenido": "En el sector turístico de Cartagena es práctica comercial otorgar descuentos del 10% por pagos anticipados en temporada baja."
    },
    {
        "ciudad": "Bucaramanga",
        "tipo": "Industrial",
        "contenido": "En Bucaramanga, las empresas del sector calzado tienen la costumbre de otorgar 60 días de plazo para el pago de mercancías."
    },
    {
        "ciudad": "Pereira",
        "tipo": "Cafetero",
        "contenido": "En la región cafetera de Pereira es costumbre liquidar las compras de café pergamino los días miércoles de cada semana."
    },
    {
        "ciudad": "Manizales",
        "tipo": "Cafetero",
        "contenido": "En Manizales es práctica comercial que los contratos de compraventa de café incluyan cláusula de ajuste por humedad."
    },
    {
        "ciudad": "Santa Marta",
        "tipo": "Portuario",
        "contenido": "En el puerto de Santa Marta es costumbre que los servicios de carga y descarga se liquiden por tonelada métrica."
    },
    {
        "ciudad": "Ibagué",
        "tipo": "Comercial",
        "contenido": "En Ibagué es práctica mercantil común que las ventas al por mayor incluyan descuentos por volumen superiores a 100 unidades."
    },
    {
        "ciudad": "Cúcuta",
        "tipo": "Fronterizo",
        "contenido": "En la zona fronteriza de Cúcuta es costumbre que las transacciones comerciales se realicen en pesos colombianos y bolívares."
    },
    {
        "ciudad": "Villavicencio",
        "tipo": "Agropecuario",
        "contenido": "En Villavicencio, sector ganadero, es práctica común que las compraventas de ganado se realicen con pesaje en báscula certificada."
    },
    {
        "ciudad": "Pasto",
        "tipo": "Comercial",
        "contenido": "En Pasto es costumbre comercial que las ferias y mercados públicos operen descuentos especiales los días domingos."
    },
    {
        "ciudad": "Armenia",
        "tipo": "Cafetero",
        "contenido": "En Armenia es práctica del sector cafetero que los anticipos por cosecha no excedan el 70% del valor estimado de la producción."
    },
    {
        "ciudad": "Popayán",
        "tipo": "Comercial",
        "contenido": "En Popayán es costumbre mercantil que durante Semana Santa se suspendan las actividades comerciales y se extiendan automáticamente los plazos de pago."
    }
]

def create_sample_data(app, db, Costumbre):
    """
    Crea datos de muestra en la base de datos si está vacía
    """
    with app.app_context():
        # Verificar si ya hay datos
        if Costumbre.query.count() == 0:
            print("🌱 Creando datos de muestra...")
            
            for data in SAMPLE_DATA:
                costumbre = Costumbre(
                    ciudad=data["ciudad"],
                    tipo=data["tipo"],
                    contenido=data["contenido"]
                )
                db.session.add(costumbre)
            
            try:
                db.session.commit()
                print(f"✅ Se crearon {len(SAMPLE_DATA)} costumbres de muestra")
            except Exception as e:
                print(f"❌ Error al crear datos de muestra: {e}")
                db.session.rollback()
        else:
            print(f"ℹ️ Base de datos ya contiene {Costumbre.query.count()} registros")
