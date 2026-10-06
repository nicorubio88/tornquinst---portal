# App de Android (TWA) del portal Tornquist

- `twa-manifest.json`: configuración (paquete `ar.com.papeleradelsur.tornquist`, Android 7 a 16, SDK objetivo 36).
- Al hacer push en `twa/` corre `.github/workflows/android.yml`: genera el proyecto con Bubblewrap, compila y deja el
  APK **sin firmar y alineado** en `descargas/sin-firmar/`.
- La firma se hace fuera de GitHub (la llave no se guarda en el repositorio, que es público):
  `python3 twa/firmar_apk.py descargas/sin-firmar/Sistemas-Tornquist-sin-firmar.apk descargas/Sistemas-Tornquist.apk clave.pem certificado.der`
- `/.well-known/assetlinks.json` declara la huella de esa llave: así la app abre el portal a pantalla completa.
- **Para publicar una versión nueva**: subir `appVersionCode` (+1) y `appVersion` en `twa-manifest.json` y firmar con la MISMA llave
  (si se pierde la llave, los celulares no aceptan la actualización y hay que desinstalar e instalar de nuevo).
