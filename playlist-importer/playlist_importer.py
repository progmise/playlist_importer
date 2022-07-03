import csv
import os
import spotify_script as spotify
import youtube_script as youtube

from googleapiclient.discovery import Resource
from io import TextIOWrapper
from re import findall, sub, IGNORECASE
from tekore import Spotify
from time import sleep


def es_texto_valido(texto: str) -> bool:

    flag_texto_valido: bool = False

    if not texto.isspace():

        if texto:
            flag_texto_valido = True

        else:
            print(f'\n¡El texto está vacío, se debe ingresar algo!')

    else:
        print(f'\n¡No se pueden ingresar solamente espacios!')

    return flag_texto_valido


def es_numero_entero(numero: str) -> bool:

    numero_formateado: str = str()
    es_numero_valido: bool = bool()

    numero_formateado = sub('[a-zA-Z]+', '', numero)

    try:
        int(numero_formateado)
        es_numero_valido = True

    except ValueError:
        print('\n¡Sólo se pueden ingresar numeros!')
        es_numero_valido = False

    return es_numero_valido


def es_opcion_valida(opcion: str, opciones: list) -> bool:

    numero_de_opcion: int = int()
    flag_opcion_valida: bool = False

    if opcion.isnumeric():
        numero_de_opcion = int(opcion)

        if numero_de_opcion > 0 and numero_de_opcion <= len(opciones):
            flag_opcion_valida = True

        else:
            print(f'\n¡Sólo puedes ingresar una opción entre el 1 y el {len(opciones)}!')

    else:
        print(f'\n¡Las opciones son numeros enteros, sin decimales!')

    return flag_opcion_valida


def validar_texto_ingresado(mensaje_a_mostrar: str) -> str:

    texto_ingresado: str = str()
    flag_texto_valido: bool = True

    while flag_texto_valido:

        texto_ingresado = input(f'\n{mensaje_a_mostrar}: ')

        if es_texto_valido(texto_ingresado):
            flag_texto_valido = False

    return texto_ingresado


def validar_opcion_ingresada(opciones: list) -> str:

    opcion_ingresada: str = str()
    flag_numero_entero_valido: bool = False
    flag_opcion_valida: bool = False

    while not (flag_numero_entero_valido and flag_opcion_valida):

        opcion_ingresada = input('\nIngrese una opción: ')

        flag_numero_entero_valido = es_numero_entero(opcion_ingresada)

        flag_opcion_valida = es_opcion_valida(opcion_ingresada, opciones)

    return opcion_ingresada


def obtener_entrada_usuario(opciones: list) -> str:

    opcion: str = str()

    print('\nOpciones válidas: \n')

    for x in range(len(opciones)):
        print(x + 1, '-', opciones[x])

    opcion = validar_opcion_ingresada(opciones)

    return opcion


def eliminar_archivo(ruta_de_archivo: str) -> None:

    if os.path.exists(ruta_de_archivo):
        os.remove(ruta_de_archivo)
        print('\nEl archivo fue eliminado satisfactoriamente\n')

    else:
        print('\n¡El archivo no existe!\n')


def leer_archivo_csv(ruta_de_archivo: str) -> 'list[str]':

    datos: list = list()
    archivo: TextIOWrapper = open(ruta_de_archivo, 'r', encoding='utf-8')

    try:
        with archivo:
            csv_lector = csv.reader(archivo, delimiter=',', quoting=csv.QUOTE_NONNUMERIC,)
        
            for dato in csv_lector:
                datos.append(dato)

    except IOError:
        print('\nNo se pudo leer el archivo: ', ruta_de_archivo)
    
    finally:
        archivo.close()

    return datos


def escribir_archivo_csv(ruta_de_archivo: str, encabezados: list, contenido: list) -> None:

    archivo: TextIOWrapper = open(ruta_de_archivo, 'w', encoding='utf-8')

    try:
        with archivo:
            csv_escritor = csv.writer(archivo, quoting=csv.QUOTE_NONNUMERIC, lineterminator='\n')

            csv_escritor.writerow(encabezados)
            csv_escritor.writerows(contenido)

    except IOError:
        print('\nNo se pudo escribir el archivo: ', ruta_de_archivo)

    finally:
        archivo.close()     


def normalizar_nombre_de_cancion(nombre_de_cancion: str) -> str:

    nombre_de_cancion_normalizada: str = str()
    cadenas_coincidentes: list = findall(r'^[^\(|\[|\{|\-]+', nombre_de_cancion)

    nombre_de_cancion_normalizada = cadenas_coincidentes[0]
    nombre_de_cancion_normalizada = sub(
        r'\b(?:feat|ft)\b(.*)',
        '',
        nombre_de_cancion_normalizada,
        flags=IGNORECASE
    ).strip()

    return nombre_de_cancion_normalizada


def normalizar_datos_de_items(datos: list) -> tuple:

    encabezados_de_items: list = list()
    datos_de_items: list = list()

    encabezados_de_items = datos[0:1][0]
    datos_de_items = datos[1:]

    return encabezados_de_items, datos_de_items


def convertir_dato_a_item(dato_de_item: list, encabezados_de_item: list) -> dict:

    item: dict = dict()

    for indice in range(len(encabezados_de_item)):

        if isinstance(dato_de_item[indice], float):
            item[encabezados_de_item[indice].lower()] = int(dato_de_item[indice])

        else:
            item[encabezados_de_item[indice].lower()] = dato_de_item[indice]

    return item


def procesar_archivo_csv(ruta_de_archivo: str) -> list:

    items: list = list()
    encabezados_de_item: list = list()
    datos_de_items: list = list()
    datos: list = leer_archivo_csv(ruta_de_archivo)

    encabezados_de_item, datos_de_items = normalizar_datos_de_items(datos)    

    for datos_de_item in datos_de_items:
        items.append(
            convertir_dato_a_item(datos_de_item, encabezados_de_item)
        )

    return items


def mostrar_lista_de_diccionarios(playlists: dict, titulo: str, tipo_de_elemento: str) -> None:

    print(f'\n{titulo}: ')

    for x in range(len(playlists)):
        print(f'\n  {x + 1}° {tipo_de_elemento}: ')

        for key, value in playlists[x].items():
            print(' '*4, f'{key} - {value}')


def mostrar_canciones_de_playlist_de_spotify(servicio: Spotify, usuario: dict) -> None:

    playlists: list = list()
    playlist: list = list()
    nombres_de_playlists: list = list()
    opcion: int = int()

    playlists = spotify.obtener_playlists(servicio, usuario.get('id', str()))
    nombres_de_playlists = [x.get('nombre', str()) for x in playlists]

    opcion = int(obtener_entrada_usuario(nombres_de_playlists)) - 1

    playlist = spotify.obtener_playlist(servicio, playlists[opcion].get('id', str()))

    mostrar_lista_de_diccionarios(playlist, 'Lista de canciones', 'canción')


def mostrar_playlists_de_spotify(servicio: Spotify, usuario: dict) -> None:

    playlists: list = spotify.obtener_playlists(servicio, usuario.get('id', str()))

    mostrar_lista_de_diccionarios(playlists, 'Listas de reproducción', 'playlist')


def crear_playlist_de_spotify(servicio: Spotify, usuario: dict) -> None:

    nombre_de_playlist: str = validar_texto_ingresado('Ingrese el nombre de la nueva playlist')
    descripcion: str = validar_texto_ingresado('Ingrese la descripción de la nueva playlist')

    spotify.crear_playlist(servicio, usuario.get('id', str()), nombre_de_playlist, descripcion)


def agregar_una_cancion_a_una_playlist_de_spotify(servicio: Spotify, usuario: dict) -> None:

    playlists: list = list()
    nombres_de_playlists: list = list()
    canciones_a_agregar: list = list()
    uris_de_canciones: list = list()
    opcion_de_playlist: int = int()
    entrada: str = str()
    flag_agregar_canciones: bool = True
    se_agregaron_las_canciones: bool = False

    playlists = spotify.obtener_playlists(servicio, usuario.get('id', str()))
    nombres_de_playlists = [x.get('nombre', str()) for x in playlists]

    opcion_de_playlist = int(obtener_entrada_usuario(nombres_de_playlists)) - 1

    while flag_agregar_canciones:

        nombre_de_cancion: str = validar_texto_ingresado('Ingrese el nombre de la canción')
        artista: str = validar_texto_ingresado('Ingrese el artista de la canción')

        canciones_encontradas: list = spotify.buscar_cancion(servicio, f'{nombre_de_cancion} {artista}')
        nombres_de_canciones: list = [
            f'{x.get("nombre_de_cancion", str())} - {x.get("artista", str())}' for x in canciones_encontradas
        ]

        opcion_de_cancion = int(obtener_entrada_usuario(nombres_de_canciones)) - 1

        canciones_a_agregar.append(canciones_encontradas[opcion_de_cancion])

        entrada = input('\n¿Quiere seguir ingresando canciones a la playlist (S/N)?: ').upper()

        if entrada not in ['S', 'Y', 'SI', 'YES']:
            flag_agregar_canciones = False

    uris_de_canciones = [x.get('uri', str()) for x in canciones_a_agregar]

    se_agregaron_las_canciones = spotify.agregar_canciones_a_playlist(
        servicio, 
        playlists[opcion_de_playlist].get('id', str()), 
        uris_de_canciones
    )

    if se_agregaron_las_canciones:
        print('\n¡Se agregaron satisfactoriamente las canciones a la playlist!\n')

    else:
        print('\n¡Hubo un error y no se agregaron las canciones a la playlist!\n')


def exportar_playlist_a_csv(playlist: list, ruta_de_archivo: str) -> None:

    canciones: list = [list(x.values()) for x in playlist]
    encabezados: list = [list(x.keys()) for x in playlist]
    encabezados = encabezados[0]
    encabezados = [x.upper() for x in encabezados]    

    escribir_archivo_csv(ruta_de_archivo, encabezados, canciones)


def exportar_playlist_de_spotify(servicio: Spotify, playlist_a_exportar: dict) -> None:
    
    playlist: list = spotify.obtener_playlist(servicio, playlist_a_exportar.get('id', str()))

    for item in playlist:
        item['nombre_de_cancion'] = normalizar_nombre_de_cancion(item.get('nombre_de_cancion', str()))
        item['nombre_de_playlist'] = playlist_a_exportar.get('nombre', str())
        item['descripcion_de_playlist'] = playlist_a_exportar.get('descripcion', str())

    exportar_playlist_a_csv(playlist, 'data\\spotify_to_youtube.csv')


def importar_playlist_a_youtube(servicio: Resource) -> None:

    playlist: dict = dict()
    videos_a_agregar: list = list()
    items_de_playlist: list = procesar_archivo_csv('data\\spotify_to_youtube.csv')
    se_importo_la_playlist_completa: bool = False

    playlist = youtube.crear_playlist(
        servicio, 
        items_de_playlist[0].get('nombre_de_playlist', str()), 
        items_de_playlist[0].get('descripcion_de_playlist', str())
    )

    for item in items_de_playlist:
        videos_encontrados: list = youtube.buscar_video(
            servicio, 
            f'{item.get("nombre_de_cancion", str())} {item.get("artista", str())}'
        )

        videos_a_agregar.append(videos_encontrados[0])

    se_importo_la_playlist_completa = youtube.agregar_elementos_a_playlist(
        servicio, 
        playlist.get('id', str()), 
        videos_a_agregar
    )

    if se_importo_la_playlist_completa:
        print('\n¡Se importó satisfactoriamente la playlist a YouTube!\n')

    else:
        print('\n¡Hubo un error y no se importó toda la playlist a YouTube!\n')


def mostrar_videos_de_playlist_de_youtube(servicio: Resource) -> None:

    playlists: list = list()
    playlist: list = list()
    nombres_de_playlists: list = list()
    opcion: int = int()

    playlists = youtube.obtener_playlists(servicio)
    nombres_de_playlists = [x.get('nombre', str()) for x in playlists]

    opcion = int(obtener_entrada_usuario(nombres_de_playlists)) - 1

    playlist = youtube.obtener_playlist(servicio, playlists[opcion].get('id', str()))

    mostrar_lista_de_diccionarios(playlist, 'Lista de videos', 'video')


def mostrar_playlists_de_youtube(servicio: Resource) -> None:

    playlists: list = youtube.obtener_playlists(servicio)

    mostrar_lista_de_diccionarios(playlists, 'Listas de reproducción', 'playlist')    


def crear_playlist_de_youtube(servicio: Resource) -> None:

    nombre_de_playlist: str = validar_texto_ingresado('Ingrese el nombre de la nueva playlist')
    descripcion: str = validar_texto_ingresado('Ingrese la descripción de la nueva playlist')

    youtube.crear_playlist(servicio, nombre_de_playlist, descripcion)


def agregar_un_elemento_a_una_playlist_de_youtube(servicio: Resource) -> None:

    playlists: list = list()
    nombres_de_playlists: list = list()
    videos_a_agregar: list = list()
    opcion_de_playlist: int = int()
    entrada: str = str()
    flag_agregar_elementos: bool = True
    se_agregaron_los_elementos: bool = False

    playlists = youtube.obtener_playlists(servicio)
    nombres_de_playlists = [x.get('nombre', str()) for x in playlists]

    opcion_de_playlist = int(obtener_entrada_usuario(nombres_de_playlists)) - 1

    while flag_agregar_elementos:

        nombre_de_cancion: str = validar_texto_ingresado('Ingrese el nombre de la canción')
        artista: str = validar_texto_ingresado('Ingrese el artista de la canción')

        videos_encontrados: list = youtube.buscar_video(servicio, f'{nombre_de_cancion} {artista}')
        nombres_de_videos: list = [x.get('nombre_de_video', str()) for x in videos_encontrados]

        opcion_de_video = int(obtener_entrada_usuario(nombres_de_videos)) - 1

        videos_a_agregar.append(videos_encontrados[opcion_de_video])

        entrada = input('\n¿Quiere seguir ingresando elementos a la playlist (S/N)?: ').upper()

        if entrada not in ['S', 'Y', 'SI', 'YES']:
            flag_agregar_elementos = False

    se_agregaron_los_elementos = youtube.agregar_elementos_a_playlist(
        servicio, 
        playlists[opcion_de_playlist].get('id', str()), 
        videos_a_agregar
    )

    if se_agregaron_los_elementos:
        print('\n¡Se agregaron satisfactoriamente los elementos a la playlist!\n')

    else:
        print('\n¡Hubo un error y no se agregaron los elementos a la playlist!\n')


def exportar_playlist_de_youtube(servicio: Resource, playlist_a_exportar: dict) -> None:
    
    playlist: list = youtube.obtener_playlist(servicio, playlist_a_exportar.get('id', str()))

    for item in playlist:
        item['nombre_de_cancion'] = normalizar_nombre_de_cancion(item.get('nombre_de_cancion', str()))
        item['nombre_de_playlist'] = playlist_a_exportar.get('nombre', str())
        item['descripcion_de_playlist'] = playlist_a_exportar.get('descripcion', str())

    exportar_playlist_a_csv(playlist, 'data\\youtube_to_spotify.csv')


def importar_playlist_a_spotify(servicio: Spotify, usuario: dict) -> None:

    playlist: dict = dict()
    canciones_a_agregar: list = list()
    uris_de_canciones: list = list()
    items_de_playlist: list = procesar_archivo_csv('data\\youtube_to_spotify.csv')
    se_importo_la_playlist_completa: bool = False

    playlist = spotify.crear_playlist(
        servicio,
        usuario.get('id', str()),
        items_de_playlist[0].get('nombre_de_playlist', str()), 
        items_de_playlist[0].get('descripcion_de_playlist', str())
    )

    for item in items_de_playlist:
        canciones_encontradas: list = spotify.buscar_cancion(
            servicio, 
            f'{item.get("nombre_de_cancion", str())} {item.get("artista", str())}'
        )

        canciones_a_agregar.append(canciones_encontradas[0])

    uris_de_canciones = [x.get('uri', str()) for x in canciones_a_agregar]

    se_importo_la_playlist_completa = spotify.agregar_canciones_a_playlist(
        servicio, 
        playlist.get('id', str()), 
        uris_de_canciones
    )

    if se_importo_la_playlist_completa:
        print('\n¡Se importó satisfactoriamente la playlist a Spotify!\n')

    else:
        print('\n¡Hubo un error y no se importó toda la playlist a Spotify!\n')


def exportar_playlist(servicio_de_spotify: Spotify, usuario: dict, 
                      servicio_de_youtube: Resource, desde: str) -> None:

    nombres_de_playlists_de_spotify: list = list()
    nombres_de_playlists_de_youtube: list = list()
    playlists_de_spotify: list = spotify.obtener_playlists(
        servicio_de_spotify, 
        usuario.get('id', str())
    )
    playlists_de_youtube: list = youtube.obtener_playlists(servicio_de_youtube)
    opcion_de_playlist: int = int()
    nombre_de_playlist_a_exportar: str = str()

    if desde == 'spotify':
        nombres_de_playlists_de_spotify = [x.get('nombre', str()) for x in playlists_de_spotify]

        opcion_de_playlist = int(obtener_entrada_usuario(nombres_de_playlists_de_spotify)) - 1

        nombre_de_playlist_a_exportar = playlists_de_spotify[opcion_de_playlist].get('nombre', str())

        nombres_de_playlists_de_youtube = [x.get('nombre', str()) for x in playlists_de_youtube]

        if nombre_de_playlist_a_exportar not in nombres_de_playlists_de_youtube:
            exportar_playlist_de_spotify(
                servicio_de_spotify,
                playlists_de_spotify[opcion_de_playlist]
            )
            importar_playlist_a_youtube(servicio_de_youtube)

        else:
            print(f"\n¡La playlist '{nombre_de_playlist_a_exportar}', ya existe en YouTube")

    elif desde == 'youtube':
        nombres_de_playlists_de_youtube = [x.get('nombre', str()) for x in playlists_de_youtube]

        opcion_de_playlist = int(obtener_entrada_usuario(nombres_de_playlists_de_youtube)) - 1

        nombre_de_playlist_a_exportar = playlists_de_youtube[opcion_de_playlist].get('nombre', str())

        nombres_de_playlists_de_spotify = [x.get('nombre', str()) for x in playlists_de_spotify]

        if nombre_de_playlist_a_exportar not in nombres_de_playlists_de_spotify:
            exportar_playlist_de_youtube(
                servicio_de_youtube,
                playlists_de_youtube[opcion_de_playlist]
            )
            importar_playlist_a_spotify(servicio_de_spotify, usuario)

        else:
            print(f"\n¡La playlist '{nombre_de_playlist_a_exportar}', ya existe en Spotify")     


def iniciar_menu_de_spotify() -> None:

    opciones: list = [
        'Crear nueva playlist',
        'Listar playlists',
        'Listar canciones de playlist',
        'Agregar canción a una playlist',
        'Exportar playlist a Youtube',
        'Cerrar sesión',
        'Volver'
    ]

    se_cerro_sesion: bool = False
    servicio_de_spotify: Spotify = spotify.obtener_servicio()
    usuario: dict = spotify.obtener_usuario_actual(servicio_de_spotify)

    print('\n######## Spotify ########')

    opcion: int = int(obtener_entrada_usuario(opciones))

    while opcion != 7:

        if se_cerro_sesion:
            servicio_de_spotify = spotify.obtener_servicio()
            usuario = spotify.obtener_usuario_actual(servicio_de_spotify)
            se_cerro_sesion = False

        if opcion == 1:
            crear_playlist_de_spotify(servicio_de_spotify, usuario)

            sleep(1)

            mostrar_playlists_de_spotify(servicio_de_spotify, usuario)            

        elif opcion == 2:
            mostrar_playlists_de_spotify(servicio_de_spotify, usuario)

        elif opcion == 3:
            mostrar_canciones_de_playlist_de_spotify(servicio_de_spotify, usuario)

        elif opcion == 4:
            agregar_una_cancion_a_una_playlist_de_spotify(servicio_de_spotify, usuario)

        elif opcion == 5:
            servicio_de_youtube: Resource = youtube.obtener_servicio()

            exportar_playlist(servicio_de_spotify, usuario, servicio_de_youtube, 'spotify')

        elif opcion == 6:
            eliminar_archivo(spotify.ARCHIVO_TEKORE)
            se_cerro_sesion = True

        print('\n######## Spotify ########')

        opcion = int(obtener_entrada_usuario(opciones))    


def iniciar_menu_de_youtube() -> None:

    opciones: list = [
        'Crear nueva playlist',
        'Listar playlists',
        'Listar videos de playlist',
        'Agregar video a una playlist',
        'Exportar playlist a Spotify',
        'Cerrar sesión',
        'Volver'
    ]

    se_cerro_sesion: bool = False
    servicio_de_youtube: Resource = youtube.obtener_servicio()

    print('\n######## YouTube ########')

    opcion: int = int(obtener_entrada_usuario(opciones))

    while opcion != 7:

        if se_cerro_sesion:
            servicio_de_youtube = youtube.obtener_servicio()
            se_cerro_sesion = False

        if opcion == 1:
            crear_playlist_de_youtube(servicio_de_youtube)

            sleep(5)

            mostrar_playlists_de_youtube(servicio_de_youtube)          

        elif opcion == 2:
            mostrar_playlists_de_youtube(servicio_de_youtube)

        elif opcion == 3:
            mostrar_videos_de_playlist_de_youtube(servicio_de_youtube)

        elif opcion == 4:
            agregar_un_elemento_a_una_playlist_de_youtube(servicio_de_youtube)

        elif opcion == 5:
            servicio_de_spotify: Spotify = spotify.obtener_servicio()
            usuario: dict = spotify.obtener_usuario_actual(servicio_de_spotify)

            exportar_playlist(servicio_de_spotify, usuario, servicio_de_youtube, 'youtube')

        elif opcion == 6:
            eliminar_archivo(youtube.ARCHIVO_TOKEN)
            se_cerro_sesion = True

        print('\n######## YouTube ########')

        opcion = int(obtener_entrada_usuario(opciones))    


def main() -> None:

    opciones: list = [
        'Spotify',
        'Youtube',
        'Cerrar sesiones',
        'Salir'
    ]

    print('\n######## Menú Principal ########')

    opcion: int = int(obtener_entrada_usuario(opciones))

    while opcion != 4:

        if opcion == 1:
            iniciar_menu_de_spotify()

        elif opcion == 2:
            iniciar_menu_de_youtube()

        elif opcion == 3:
            eliminar_archivo(spotify.ARCHIVO_TEKORE)
            eliminar_archivo(youtube.ARCHIVO_TOKEN)        

        print('\n######## Menú Principal ########')

        opcion = int(obtener_entrada_usuario(opciones))

    print('\nPrograma finalizado')


if __name__ == '__main__':
    main()